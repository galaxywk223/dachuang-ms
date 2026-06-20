#!/usr/bin/env node

import { spawn } from "node:child_process";
import { mkdir, rm, writeFile } from "node:fs/promises";
import http from "node:http";
import https from "node:https";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("../.local/playwright-runner/node_modules/playwright");

const SCRIPT_DIR = path.dirname(fileURLToPath(import.meta.url));
const ROOT_DIR = path.resolve(SCRIPT_DIR, "..");
const BACKEND_DIR = path.join(ROOT_DIR, "backend");
const FRONTEND_DIR = path.join(ROOT_DIR, "frontend");
const PYTHON = process.env.DACHUANG_PYTHON || (process.platform === "win32"
  ? path.join(BACKEND_DIR, "venv", "Scripts", "python.exe")
  : path.join(BACKEND_DIR, "venv", "bin", "python"));
const OUT_DIR = path.join(ROOT_DIR, "docs", "screenshots");
const API_BASE_URL = process.env.DACHUANG_API_BASE_URL || "http://127.0.0.1:8000";
const FRONTEND_URL = process.env.DACHUANG_FRONTEND_URL || "http://127.0.0.1:3000";
const STARTUP_TIMEOUT_MS = Number(process.env.DACHUANG_SCREENSHOT_TIMEOUT_MS || "120000");
const ROUTE_WAIT_MS = Number(process.env.DACHUANG_SCREENSHOT_WAIT_MS || "1800");
const PASSWORD = process.env.DACHUANG_DEMO_PASSWORD;
const DEMO_USERS = {
  level1: process.env.DACHUANG_LEVEL1_USER,
  level2: process.env.DACHUANG_LEVEL2_USER,
  student: process.env.DACHUANG_STUDENT_USER,
};
const DEMO_PROJECT_NO = process.env.DACHUANG_DEMO_PROJECT_NO;
const DEMO_BATCH_CODE = process.env.DACHUANG_DEMO_BATCH_CODE;
const VERBOSE = process.env.DACHUANG_SCREENSHOT_VERBOSE !== "0";

if (!PASSWORD) {
  console.error("DACHUANG_DEMO_PASSWORD must be set before capturing screenshots.");
  process.exit(1);
}

if (!DEMO_USERS.level1 || !DEMO_USERS.level2 || !DEMO_USERS.student) {
  console.error("DACHUANG_LEVEL1_USER, DACHUANG_LEVEL2_USER, and DACHUANG_STUDENT_USER must be set before capturing screenshots.");
  process.exit(1);
}

if (!DEMO_PROJECT_NO || !DEMO_BATCH_CODE) {
  console.error("DACHUANG_DEMO_PROJECT_NO and DACHUANG_DEMO_BATCH_CODE must be set before capturing screenshots.");
  process.exit(1);
}

const accounts = {
  level1: { employeeId: DEMO_USERS.level1, password: PASSWORD },
  level2: { employeeId: DEMO_USERS.level2, password: PASSWORD },
  student: { employeeId: DEMO_USERS.student, password: PASSWORD },
};

const screenshotPlan = [
  {
    id: "01",
    file: "01_statistics_overview.png",
    title: "统计概览",
    account: "level1",
    path: "/level1-admin/statistics",
  },
  {
    id: "02",
    file: "02_recommendation_ranking.png",
    title: "项目推荐排序",
    account: "level2",
    path: "/level2-admin/publication",
  },
  {
    id: "03",
    file: "03_publication_center.png",
    title: "立项发布中心",
    account: "level1",
    path: "/level1-admin/publication",
  },
  {
    id: "04",
    file: "04_project_detail.png",
    title: "项目详情",
    account: "level1",
    path: ({ projectId }) => `/level1-admin/projects/${projectId}`,
  },
  {
    id: "05",
    file: "05_data_center.png",
    title: "数据中心",
    account: "level1",
    path: "/level1-admin/data-center",
  },
  {
    id: "06",
    file: "06_task_center.png",
    title: "任务中心",
    account: "level1",
    path: "/level1-admin/tasks",
  },
  {
    id: "07",
    file: "07_student_achievements.png",
    title: "学生端成果管理",
    account: "student",
    path: "/achievements",
  },
  {
    id: "08",
    file: "08_student_notices.png",
    title: "学生端通知公告",
    account: "student",
    path: "/notifications?tab=notices",
  },
  {
    id: "09",
    file: "09_student_materials.png",
    title: "学生端资料下载",
    account: "student",
    path: "/notifications?tab=materials",
  },
];

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function npmDevCommand() {
  if (process.platform === "win32") {
    return {
      command: process.env.ComSpec || "cmd.exe",
      args: ["/d", "/s", "/c", "npm run dev -- --host 127.0.0.1 --port 3000"],
    };
  }
  return {
    command: "npm",
    args: ["run", "dev", "--", "--host", "127.0.0.1", "--port", "3000"],
  };
}

function spawnLogged(command, args, options = {}) {
  if (VERBOSE) {
    console.log(`Starting: ${command} ${args.join(" ")}`);
  }
  const child = spawn(command, args, {
    cwd: options.cwd || ROOT_DIR,
    env: { ...process.env, ...(options.env || {}) },
    stdio: ["ignore", "pipe", "pipe"],
  });
  const logs = [];
  const state = { child, logs, error: null };

  const remember = (source, chunk) => {
    const text = chunk.toString();
    for (const line of text.split(/\r?\n/).filter(Boolean)) {
      logs.push(`${source}: ${line}`);
    }
    if (VERBOSE) {
      const target = source === "stderr" ? process.stderr : process.stdout;
      target.write(text);
    }
    if (logs.length > 100) {
      logs.splice(0, logs.length - 100);
    }
  };

  child.stdout.on("data", (chunk) => remember("stdout", chunk));
  child.stderr.on("data", (chunk) => remember("stderr", chunk));
  child.on("error", (error) => {
    state.error = error;
    logs.push(`process error: ${error.message}`);
    if (VERBOSE) console.error(`Process error: ${error.message}`);
  });
  return state;
}

function formatLogs(state) {
  return state?.logs?.length ? `\nRecent output:\n${state.logs.join("\n")}` : "";
}

async function stopProcessTree(child) {
  if (!child || child.exitCode !== null) return;

  if (process.platform === "win32") {
    await new Promise((resolve) => {
      spawn("taskkill", ["/PID", String(child.pid), "/T", "/F"]).on("close", resolve);
    });
    return;
  }

  child.kill("SIGTERM");
  await delay(1000);
  if (child.exitCode === null) child.kill("SIGKILL");
}

async function runCommand(command, args, options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd: options.cwd || ROOT_DIR,
      env: { ...process.env, ...(options.env || {}) },
      stdio: ["ignore", "pipe", "pipe"],
    });
    let stdout = "";
    let stderr = "";
    child.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });
    child.on("close", (code) => {
      if (code === 0) {
        resolve({ stdout, stderr });
        return;
      }
      reject(new Error(`${command} ${args.join(" ")} failed with code ${code}\n${stdout}\n${stderr}`));
    });
  });
}

async function isHttpReady(url) {
  return new Promise((resolve) => {
    let settled = false;
    const finish = (value) => {
      if (settled) return;
      settled = true;
      resolve(value);
    };
    const parsed = new URL(url);
    const client = parsed.protocol === "https:" ? https : http;
    const request = client.get(parsed, (response) => {
      response.resume();
      finish((response.statusCode || 0) < 500);
    });
    request.on("error", () => finish(false));
    request.setTimeout(2000, () => {
      request.destroy();
      finish(false);
    });
  });
}

async function waitForHttp(url, state, label) {
  const deadline = Date.now() + STARTUP_TIMEOUT_MS;
  while (Date.now() < deadline) {
    if (state?.child?.exitCode !== null) {
      throw new Error(`${label} exited before becoming ready.${formatLogs(state)}`);
    }
    if (state?.error) {
      throw new Error(`${label} failed to start: ${state.error.message}.${formatLogs(state)}`);
    }
    if (await isHttpReady(url)) return;
    await delay(500);
  }
  throw new Error(`Timed out waiting for ${label}: ${url}.${formatLogs(state)}`);
}

async function seedDemoData() {
  console.log("Seeding local demo data...");
  await runCommand(PYTHON, ["manage.py", "seed_demo_data", "--password", PASSWORD], {
    cwd: BACKEND_DIR,
  });
}

async function ensureServices() {
  const states = [];
  let backendState = null;
  let frontendState = null;
  console.log("Checking backend...");
  const apiReady = await isHttpReady(`${API_BASE_URL}/api/v1/auth/login/`);
  console.log(`Backend ready: ${apiReady}`);
  if (!apiReady) {
    backendState = spawnLogged(PYTHON, ["manage.py", "runserver", "127.0.0.1:8000", "--noreload"], {
        cwd: BACKEND_DIR,
        env: { PYTHONUNBUFFERED: "1" },
      });
    states.push(backendState);
  }

  console.log("Checking frontend...");
  const frontendReady = await isHttpReady(FRONTEND_URL);
  console.log(`Frontend ready: ${frontendReady}`);
  if (!frontendReady) {
    const npmCommand = npmDevCommand();
    frontendState = spawnLogged(npmCommand.command, npmCommand.args, {
        cwd: FRONTEND_DIR,
        env: { VITE_API_BASE_URL: API_BASE_URL },
      });
    states.push(frontendState);
  }

  try {
    console.log("Waiting for backend...");
    await waitForHttp(`${API_BASE_URL}/api/v1/auth/login/`, backendState, "backend");
    console.log("Waiting for frontend...");
    await waitForHttp(FRONTEND_URL, frontendState, "frontend");
    return states;
  } catch (error) {
    for (const state of states.reverse()) {
      await stopProcessTree(state.child);
    }
    throw error;
  }
}

async function login(account) {
  console.log(`Logging in ${account.employeeId}...`);
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      employee_id: account.employeeId,
      password: account.password,
    }),
  });
  if (!response.ok) {
    throw new Error(`Login failed for ${account.employeeId}: HTTP ${response.status}`);
  }
  const payload = await response.json();
  if (payload.code !== 200 || !payload.data?.access_token) {
    throw new Error(`Login failed for ${account.employeeId}: ${JSON.stringify(payload)}`);
  }
  return payload.data;
}

function extractFirstProjectId(payload) {
  const data = payload?.data;
  const candidates = [
    data?.results,
    data?.items,
    data?.list,
    data?.data?.results,
    Array.isArray(data) ? data : null,
  ].filter(Boolean);
  for (const candidate of candidates) {
    if (Array.isArray(candidate) && candidate.length > 0) {
      return candidate[0].id || candidate[0].project || candidate[0].project_id;
    }
  }
  return null;
}

async function getDemoContext(token) {
  const projectUrl = `${API_BASE_URL}/api/v1/projects/admin/manage/?search=${encodeURIComponent(DEMO_PROJECT_NO)}&page_size=5`;
  const projectResponse = await fetch(projectUrl, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!projectResponse.ok) {
    throw new Error(`Project lookup failed: HTTP ${projectResponse.status}`);
  }
  const projectPayload = await projectResponse.json();
  const projectId = extractFirstProjectId(projectPayload);
  if (!projectId) {
    throw new Error(`Demo project not found: ${JSON.stringify(projectPayload).slice(0, 500)}`);
  }

  const batchResponse = await fetch(`${API_BASE_URL}/api/v1/system-settings/batches/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!batchResponse.ok) {
    throw new Error(`Batch lookup failed: HTTP ${batchResponse.status}`);
  }
  const batchPayload = await batchResponse.json();
  const batchList = batchPayload?.data?.results || batchPayload?.data || [];
  const currentBatch = Array.isArray(batchList)
    ? batchList.find((item) => item.code === DEMO_BATCH_CODE || item.is_current) || batchList[0]
    : null;
  if (!currentBatch?.id) {
    throw new Error(`Demo batch not found: ${JSON.stringify(batchPayload).slice(0, 500)}`);
  }

  return { projectId, batchId: currentBatch.id };
}

async function prepareSession(page, session) {
  await page.goto(FRONTEND_URL, { waitUntil: "domcontentloaded", timeout: 45000 });
  await page.evaluate((data) => {
    localStorage.clear();
    localStorage.setItem("token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    if (data.user?.role) {
      localStorage.setItem("user_role", String(data.user.role).toLowerCase());
    }
    if (data.user?.role_info) {
      localStorage.setItem("role_info", JSON.stringify(data.user.role_info));
    }
  }, session);
}

async function waitForAppPage(page) {
  await page.waitForLoadState("domcontentloaded");
  await page.waitForLoadState("networkidle", { timeout: 12000 }).catch(() => {});
  await page.waitForTimeout(ROUTE_WAIT_MS);
  await page.locator("#app").waitFor({ state: "visible", timeout: 45000 });
}

async function capture(page, item, context) {
  const routePath = typeof item.path === "function" ? item.path(context) : item.path;
  const outputPath = path.join(OUT_DIR, item.file);
  await page.goto(new URL(routePath, FRONTEND_URL).href, {
    waitUntil: "domcontentloaded",
    timeout: 45000,
  });
  await waitForAppPage(page);
  if (item.enhance) {
    await item.enhance(page, context);
    await waitForAppPage(page);
  }
  await page.screenshot({
    path: outputPath,
    fullPage: false,
    animations: "disabled",
    caret: "hide",
    scale: "css",
  });
  console.log(`Saved ${item.id} ${item.title}: ${path.relative(ROOT_DIR, outputPath)}`);
}

async function main() {
  await mkdir(OUT_DIR, { recursive: true });
  await seedDemoData();

  const serviceStates = await ensureServices();
  let browser;
  try {
    const sessions = {
      level1: await login(accounts.level1),
      level2: await login(accounts.level2),
      student: await login(accounts.student),
    };
    const context = await getDemoContext(sessions.level1.access_token);

    browser = await chromium.launch({ headless: true });
    const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
    page.setDefaultTimeout(45000);

    let currentAccount = "";
    for (const item of screenshotPlan) {
      if (item.account !== currentAccount) {
        await prepareSession(page, sessions[item.account]);
        currentAccount = item.account;
      }
      await capture(page, item, context);
    }

    const indexLines = [
      "# Dachuang-MS 自动截图清单",
      "",
      `- 生成时间：${new Date().toLocaleString("zh-CN", { hour12: false })}`,
      "",
      "| 编号 | 页面 | 文件 |",
      "|---:|---|---|",
      ...screenshotPlan.map((item) => `| ${item.id} | ${item.title} | \`${item.file}\` |`),
      "",
    ];
    await writeFile(path.join(OUT_DIR, "README.md"), `${indexLines.join("\n")}\n`, "utf8");
    console.log(`Saved ${screenshotPlan.length} screenshots to ${path.relative(ROOT_DIR, OUT_DIR)}`);
  } finally {
    if (browser) await browser.close().catch(() => {});
    for (const state of serviceStates.reverse()) {
      await stopProcessTree(state.child);
    }
  }
}

main().catch(async (error) => {
  console.error(error instanceof Error ? error.message : error);
  await rm(path.join(OUT_DIR, ".capture-failed"), { force: true }).catch(() => {});
  process.exitCode = 1;
});

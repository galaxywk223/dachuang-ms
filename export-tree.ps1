# 导出项目目录树脚本
# 使用方法: .\export-tree.ps1

# 设置输出文件
$outputFile = "project-tree.txt"

# 定义要忽略的目录和文件
$ignoreDirs = @(
    "node_modules",
    "__pycache__",
    ".git",
    ".vscode",
    ".idea",
    "venv",
    "env",
    ".venv",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    "htmlcov",
    ".coverage",
    "logs",
    ".DS_Store"
)

$ignoreFiles = @(
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".Python",
    "*.so",
    "*.egg",
    "*.egg-info",
    ".env",
    ".env.local",
    ".env.*.local",
    "*.log",
    "*.sqlite3",
    "*.db",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    ".DS_Store",
    "Thumbs.db",
    "desktop.ini"
)

# 检查是否应该忽略目录
function Should-IgnoreDirectory($dirName) {
    foreach ($ignore in $ignoreDirs) {
        if ($dirName -eq $ignore) {
            return $true
        }
    }
    return $false
}

# 检查是否应该忽略文件
function Should-IgnoreFile($fileName) {
    foreach ($pattern in $ignoreFiles) {
        if ($fileName -like $pattern) {
            return $true
        }
    }
    return $false
}

# 递归获取目录树
function Get-DirectoryTree {
    param(
        [string]$Path,
        [string]$Prefix = "",
        [bool]$IsLast = $true
    )
    
    $items = Get-ChildItem -Path $Path -Force | Where-Object { 
        -not (Should-IgnoreDirectory $_.Name) -and -not (Should-IgnoreFile $_.Name)
    } | Sort-Object { $_.PSIsContainer }, Name
    
    $count = $items.Count
    $index = 0
    
    foreach ($item in $items) {
        $index++
        $isLastItem = ($index -eq $count)
        
        # 确定连接符
        if ($isLastItem) {
            $connector = "└── "
            $extension = "    "
        } else {
            $connector = "├── "
            $extension = "│   "
        }
        
        # 输出当前项
        $line = $Prefix + $connector + $item.Name
        
        if ($item.PSIsContainer) {
            $line += "/"
        }
        
        Write-Output $line
        
        # 如果是目录，递归处理
        if ($item.PSIsContainer) {
            $newPrefix = $Prefix + $extension
            Get-DirectoryTree -Path $item.FullName -Prefix $newPrefix -IsLast $isLastItem
        }
    }
}

# 开始生成目录树
Write-Host "正在生成项目目录树..." -ForegroundColor Green

# 获取项目根目录名称
$rootDir = Split-Path -Leaf (Get-Location)

# 生成树形结构
$treeOutput = @()
$treeOutput += $rootDir + "/"
$treeOutput += Get-DirectoryTree -Path (Get-Location)

# 保存到文件
$treeOutput | Out-File -FilePath $outputFile -Encoding UTF8

Write-Host "目录树已导出到: $outputFile" -ForegroundColor Green
Write-Host "共 $($treeOutput.Count) 行" -ForegroundColor Cyan

# 显示前20行预览
Write-Host "`n预览（前20行）:" -ForegroundColor Yellow
$treeOutput | Select-Object -First 20 | ForEach-Object { Write-Host $_ }

if ($treeOutput.Count -gt 20) {
    Write-Host "..." -ForegroundColor Gray
    Write-Host "（更多内容请查看 $outputFile 文件）" -ForegroundColor Gray
}

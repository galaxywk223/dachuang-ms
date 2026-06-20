import "element-plus";

declare module "element-plus" {
  export type {
    FormRules,
  } from "element-plus/es/components/form";
  export type {
    UploadFile,
    UploadInstance,
    UploadRawFile,
    UploadUserFile,
  } from "element-plus/es/components/upload";
  export type {
    CascaderOption,
  } from "element-plus/es/components/cascader-panel/src/types";
}

declare module "element-plus/es/locale/lang/zh-cn" {
  import type { Language } from "element-plus/es/locale";

  const zhCn: Language;
  export default zhCn;
}

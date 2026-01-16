"""
Certificate rendering helpers.
"""

from apps.system_settings.models import CertificateSetting


from django.db.models import Q


def get_best_match_setting(project=None):
    """
    根据项目获取最匹配的证书配置
    优先级：
    1. 级别 + 类别 完全匹配
    2. 级别匹配 (类别为空)
    3. 类别匹配 (级别为空)
    4. 通用匹配 (级别、类别均为空)
    5. 最新启用的任意配置 (兜底)
    """
    base_qs = CertificateSetting.objects.filter(is_active=True)

    if not project:
        return base_qs.order_by("-updated_at").first()

    # 准备查询条件
    level_id = project.level_id if project.level else None
    category_id = project.category_id if project.category else None

    # 1. 级别 + 类别 完全匹配
    if level_id and category_id:
        match = (
            base_qs.filter(project_level_id=level_id, project_category_id=category_id)
            .order_by("-updated_at")
            .first()
        )
        if match:
            return match

    # 2. 级别匹配 (类别无限制)
    if level_id:
        match = (
            base_qs.filter(project_level_id=level_id, project_category__isnull=True)
            .order_by("-updated_at")
            .first()
        )
        if match:
            return match

    # 3. 类别匹配 (级别无限制)
    if category_id:
        match = (
            base_qs.filter(project_level__isnull=True, project_category_id=category_id)
            .order_by("-updated_at")
            .first()
        )
        if match:
            return match

    # 4. 通用匹配 (无限制)
    match = (
        base_qs.filter(project_level__isnull=True, project_category__isnull=True)
        .order_by("-updated_at")
        .first()
    )
    if match:
        return match

    # 5. 兜底 (最新)
    return base_qs.order_by("-updated_at").first()


def render_certificate_html(project, setting=None, request=None):
    setting = setting or get_best_match_setting(project)
    school_name = setting.school_name if setting else ""
    issuer = setting.issuer_name if setting else ""
    template_code = setting.template_code if setting else "DEFAULT"
    style_config = setting.style_config if setting else {}

    def build_asset_url(file_field):
        if not file_field:
            return ""
        try:
            url = file_field.url
            if request:
                return request.build_absolute_uri(url)
            return url
        except Exception:
            return ""

    bg_url = build_asset_url(setting.background_image) if setting else ""
    seal_url = build_asset_url(setting.seal_image) if setting else ""

    font_family = style_config.get("font_family", "SimSun")
    title_size = style_config.get("title_size", 32)
    body_size = style_config.get("body_size", 18)
    line_height = style_config.get("line_height", 1.8)
    padding = style_config.get("padding", 60)
    title_margin = style_config.get("title_margin", 24)
    canvas_width = style_config.get("canvas_width", 1123)
    canvas_height = style_config.get("canvas_height", 794)
    seal_width = style_config.get("seal_width", 140)
    seal_right = style_config.get("seal_right", 120)
    seal_bottom = style_config.get("seal_bottom", 120)
    page_size = style_config.get("page_size", "A4 landscape")
    background_image = f'url("{bg_url}")' if bg_url else "none"
    return f"""
        <html>
        <head>
          <meta charset="utf-8" />
          <title>结题证书</title>
          <style>
            @page {{
              size: {page_size};
              margin: 0;
            }}
            body {{
              font-family: "{font_family}", serif;
              margin: 0;
              background: #f5f6f8;
              display: flex;
              justify-content: center;
              align-items: center;
              min-height: 100vh;
              -webkit-print-color-adjust: exact;
              print-color-adjust: exact;
            }}
            .certificate {{
              width: {canvas_width}px;
              height: {canvas_height}px;
              background: #fff;
              position: relative;
              overflow: hidden;
              box-sizing: border-box;
              text-align: center;
              padding: {padding}px;
              background-image: {background_image};
              background-repeat: no-repeat;
              background-position: center;
              background-size: cover;
            }}
            .title {{
              font-size: {title_size}px;
              font-weight: bold;
              margin-bottom: {title_margin}px;
              letter-spacing: 4px;
            }}
            .content {{
              font-size: {body_size}px;
              line-height: {line_height};
            }}
            .issuer {{
              margin-top: 40px;
              text-align: right;
              padding-right: 80px;
            }}
            .seal {{
              position: absolute;
              right: {seal_right}px;
              bottom: {seal_bottom}px;
              width: {seal_width}px;
              opacity: 0.85;
            }}
          </style>
        </head>
        <body>
          <div class="certificate">
            <div class="title">结题证书</div>
            <div class="content">
              <p>{school_name}</p>
              <p>兹证明：{project.leader.real_name} 负责的项目《{project.title}》已通过结题验收。</p>
              <p>项目编号：{project.project_no}</p>
              <p>项目级别：{project.level.label if project.level else ""}</p>
              <p>项目类别：{project.category.label if project.category else ""}</p>
              <p>模板编号：{template_code}</p>
            </div>
            <div class="issuer">{issuer}</div>
            {f'<img class="seal" src="{seal_url}" alt="seal" />' if seal_url else ""}
          </div>
        </body>
        </html>
        """

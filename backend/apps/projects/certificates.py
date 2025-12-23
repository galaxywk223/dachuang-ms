"""
Certificate rendering helpers.
"""

from apps.system_settings.models import CertificateSetting


def get_active_certificate_setting():
    return CertificateSetting.objects.filter(is_active=True).order_by("-updated_at").first()


def render_certificate_html(project, setting=None):
    setting = setting or get_active_certificate_setting()
    school_name = setting.school_name if setting else ""
    issuer = setting.issuer_name if setting else ""
    template_code = setting.template_code if setting else "DEFAULT"
    return f"""
        <html>
        <head>
          <meta charset="utf-8" />
          <title>结题证书</title>
          <style>
            body {{ font-family: "SimSun", serif; text-align:center; padding: 40px; }}
            .title {{ font-size: 32px; font-weight: bold; margin-bottom: 24px; }}
            .content {{ font-size: 18px; line-height: 1.8; }}
          </style>
        </head>
        <body>
          <div class="title">结题证书</div>
          <div class="content">
            <p>{school_name}</p>
            <p>兹证明：{project.leader.real_name} 负责的项目《{project.title}》已通过结题验收。</p>
            <p>项目编号：{project.project_no}</p>
            <p>项目级别：{project.level.label if project.level else ""}</p>
            <p>项目类别：{project.category.label if project.category else ""}</p>
            <p>模板编号：{template_code}</p>
            <p style="margin-top:40px;">{issuer}</p>
          </div>
        </body>
        </html>
        """

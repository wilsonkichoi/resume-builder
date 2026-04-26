from __future__ import annotations

from resume_builder.models.resume import ResumeIR


def render_markdown(ir: ResumeIR) -> str:
    lines: list[str] = []

    lines.append(f"# {ir.header.name}")
    lines.append(f"**{ir.header.title}**")
    lines.append(f"{ir.header.location} | {ir.header.email} | {ir.header.linkedin} | {ir.header.github}")
    lines.append("")

    lines.append("### Professional Summary")
    lines.append(ir.summary.paragraph)
    lines.append("")
    for bullet in ir.summary.bullets:
        lines.append(f"* **{bullet.label}:** {bullet.text}")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("### Skills")
    for skill in ir.skills:
        lines.append(f"**{skill.category}:** {skill.items}")
    lines.append("")
    lines.append("---")
    lines.append("")

    lines.append("### Professional Experience")
    lines.append("")
    for company in ir.experience:
        lines.append(f"#### **{company.company}** | {company.location}")
        if company.description:
            lines.append(f"*{company.description}*")
        lines.append(f"**{company.dates}**")
        lines.append("")
        for role in company.roles:
            if role.title == "Sabbatical":
                if role.description:
                    lines.append(role.description)
                lines.append("")
                continue

            lines.append(f"**{role.title}** *({role.dates})*")
            if role.description:
                lines.append(f"*{role.description}*")
            for bullet in role.bullets:
                if bullet.label:
                    lines.append(f"* **{bullet.label}:** {bullet.text}")
                else:
                    lines.append(f"* {bullet.text}")
            lines.append("")

        lines.append("---")
        lines.append("")

    lines.append("### Personal Projects")
    lines.append("")
    for project in ir.projects:
        lines.append(f"**{project.name}** — [{project.url.replace('https://', '')}]({project.url})")
        lines.append(project.description)
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("### Education")
    lines.append(f"**{ir.education.degree}** | {ir.education.institution}")
    lines.append("")

    return "\n".join(lines)

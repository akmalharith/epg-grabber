from xml.sax.saxutils import escape


def xml_header(title):
    return """<?xml version="1.0" encoding="UTF-8"?>
<tv generator-info-name="{title}">""".format(title=title)


def xml_close():
    return "</tv>"


def program_to_xml(program):
    if not program.title:   # Don't parse if empty title
        return ""

    tag_programme = f"<programme start=\"{program.start}\" stop=\"{program.stop}\" channel=\"{program.channel_name}\">"
    tag_title = f"<title lang=\"en\">{escape(program.title)}</title>"
    tag_desc = f"<desc lang=\"en\">{escape(program.description)}</desc>"
    tag_episode = f"<episode-num system=\"onscreen\">{program.episode}</episode-num>"
    tag_category = f"<category lang=\"en\">{escape(program.category)}</desc>"
    # TODO:
    # Eg: <rating system="VCHIP"><value>TV-G</value></rating>"""
    tag_program_end = "</programme>"

    program = "\n".join([tag_programme,
                         tag_title,
                         tag_desc,
                         tag_episode,
                         tag_category,
                         tag_program_end])

    return program


def channel_to_xml(channel):
    line_channel = f"<channel id=\"{escape(channel.tvg_id)}\">"
    line_display_name = f"<display-name lang=\"en\">{escape(channel.tvg_name)}</display-name>"
    line_icon = f"<icon src=\"{escape(channel.tvg_logo)}\"/>"
    line_channel_end = "</channel>"

    channel_xml = "\n".join(
        [line_channel, line_display_name, line_icon, line_channel_end])

    return channel_xml

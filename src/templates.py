from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

TEMPLATE_DIR = Path(__file__).parent / "templates"
_jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(),
    cache_size=0,  # disable cache to avoid hashability issues
)


def render_template(name: str, **context) -> str:
    template = _jinja_env.get_template(name)
    return template.render(**context)

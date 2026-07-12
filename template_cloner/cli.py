# template_cloner/cli.py

import click
from .extractor import extract_template
from .applier import apply_template

@click.group()
def cli():
    """KiCad Template Cloner — клонирование участков PCB"""
    pass

@cli.command()
@click.option('--output', '-o', default='template.yaml', help='Выходной файл шаблона')
def extract(output):
    """Извлечь шаблон из выделенной области"""
    click.echo(f"Извлечение шаблона в {output}...")
    extract_template(output)
    click.echo("Готово!")

@cli.command()
@click.option('--input', '-i', default='template.yaml', help='Файл шаблона')
@click.option('--origin-x', type=float, required=True, help='Новая координата X')
@click.option('--origin-y', type=float, required=True, help='Новая координата Y')
def place(input, origin_x, origin_y):
    """Применить шаблон в новой позиции"""
    click.echo(f"Применение шаблона из {input} в ({origin_x}, {origin_y})...")
    apply_template(input, origin_x, origin_y)
    click.echo("Готово!")

if __name__ == '__main__':
    cli()
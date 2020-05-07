from gns3fy.drawing_utils import (
    generate_ellipse_svg,
    generate_line_svg,
    generate_rectangle_svg,
    parsed_x,
    parsed_y,
)


def test_generate_rectangle_svg():
    rectangle = generate_rectangle_svg()
    assert rectangle == (
        '<svg height="100" width="200"><rect fill="#ffffff" fill-opacity="1.0" '
        'height="100" stroke="#000000" stroke-width="2" width="200" /></svg>'
    )


def test_generate_ellipse_svg():
    rectangle = generate_ellipse_svg()
    assert rectangle == (
        '<svg height="200.0" width="200.0"><ellipse cx="100" cy="100" fill="#ffffff" '
        'fill-opacity="1.0" rx="100" ry="100" stroke="#000000" stroke-width="2" />'
        "</svg>"
    )


def test_generate_line_svg():
    rectangle = generate_line_svg()
    assert rectangle == (
        '<svg height="0" width="200"><line stroke="#000000" stroke-width="2" x1="0" '
        'x2="200" y1="0" y2="0" /></svg>'
    )


def test_parsed_x():
    x_value = parsed_x(x=7)
    assert x_value == 700


def test_parsed_y():
    y_value = parsed_y(y=7)
    assert y_value == -700

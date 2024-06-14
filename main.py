import flet as ft


class SampleRod(ft.BarChartRod):
    def __init__(self, y: float, hovered: bool = False):
        super().__init__()
        self.hovered = hovered
        self.y = y

    def _before_build_command(self):
        self.to_y = self.y + 1 if self.hovered else self.y
        self.color = "#76ffd5" if self.hovered else "#eeff71"
        self.border_side = (
            ft.BorderSide(width=1, color=ft.colors.WHITE)
            if self.hovered
            else ft.BorderSide(width=0, color=ft.colors.WHITE)
        )
        super()._before_build_command()

    def _build(self):
        self.tooltip = str(self.y)
        self.width = 22
        self.color = ft.colors.WHITE
        self.bg_to_y = 50
        self.bg_color = "#5a6400"


def main(page: ft.Page):
    page.title = "Odoo Delivery App"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.bgcolor = "#F1F2F7"

    def on_chart_event(e: ft.BarChartEvent):
        for group_index, group in enumerate(chart.bar_groups):
            for rod_index, rod in enumerate(group.bar_rods):
                rod.hovered = e.group_index == group_index and e.rod_index == rod_index
        chart.update()

    chart = chart = ft.BarChart(
            height=150,
            bgcolor="#006b54",
            bar_groups=[
                ft.BarChartGroup(
                    x=0,
                    bar_rods=[SampleRod(8)],
                ),
                ft.BarChartGroup(
                    x=1,
                    bar_rods=[SampleRod(6.5)],
                ),
                ft.BarChartGroup(
                    x=2,
                    bar_rods=[SampleRod(5)],
                ),
                ft.BarChartGroup(
                    x=3,
                    bar_rods=[SampleRod(7.5)],
                ),
                ft.BarChartGroup(
                    x=4,
                    bar_rods=[SampleRod(9)],
                ),
                ft.BarChartGroup(
                    x=5,
                    bar_rods=[SampleRod(11.5)],
                ),
            ],
            bottom_axis=ft.ChartAxis(
                labels=[
                    ft.ChartAxisLabel(value=0, label=ft.Text("Jan", color="#76ffd5")),
                    ft.ChartAxisLabel(value=1, label=ft.Text("Feb", color="#76ffd5")),
                    ft.ChartAxisLabel(value=2, label=ft.Text("Mar", color="#76ffd5")),
                    ft.ChartAxisLabel(value=3, label=ft.Text("Apr", color="#76ffd5")),
                    ft.ChartAxisLabel(value=4, label=ft.Text("May", color="#76ffd5")),
                    ft.ChartAxisLabel(value=5, label=ft.Text("Jun", color="#76ffd5")),
                ],
            ),
            on_chart_event=on_chart_event,
            interactive=True,
        )

    page.add(
        ft.Container(
            margin=ft.margin.all(5),
            border_radius=20,
            bgcolor="#006b54",
            padding=10,
            height=150,
            content=chart
        )
    )

    page.go(page.route)


ft.app(main, assets_dir='assets')

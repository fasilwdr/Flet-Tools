import flet as ft
from colors import PRIMARY, PRIMARY_CONTAINER, SECONDARY, SECONDARY_CONTAINER, TERTIARY, TERTIARY_CONTAINER


def UserError(page, text):
    snackbar = ft.SnackBar(content=ft.Text(text, color=ft.colors.WHITE, text_align="center"), open=True, bgcolor=ft.colors.RED)
    page.show_snack_bar(snackbar)


def UserInfo(page, text):
    snackbar = ft.SnackBar(content=ft.Text(text, color=ft.colors.WHITE, text_align="center"), open=True, bgcolor=ft.colors.BLUE)
    page.show_snack_bar(snackbar)


def UserWarning(page, text):
    snackbar = ft.SnackBar(content=ft.Text(text, color=ft.colors.BLACK, text_align="center"), open=True, bgcolor=ft.colors.YELLOW)
    page.show_snack_bar(snackbar)

class SampleRod(ft.BarChartRod):
    def __init__(self, y: float, hovered: bool = False):
        super().__init__()
        self.hovered = hovered
        self.y = y

    def _before_build_command(self):
        self.to_y = self.y + 1 if self.hovered else self.y
        self.color = TERTIARY_CONTAINER if self.hovered else SECONDARY_CONTAINER
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
        self.bg_color = SECONDARY


class Splash(ft.Container):
    def __init__(self):
        super().__init__()
        self.alignment = ft.alignment.center
        self.content = ft.CupertinoActivityIndicator(radius=20, color=ft.colors.RED)


class SummaryCard(ft.Container):
    def __init__(self, title="", subtitle="", ref=None, bgcolor=ft.colors.PRIMARY_CONTAINER, col=None, icon=None,
                 img_path=None, data=None, color=ft.colors.PRIMARY, **kwargs):
        super().__init__(**kwargs)
        # Custom Properties
        self.data = data
        self.title = title
        self.subtitle = subtitle
        self.icon = icon
        self.img_path = img_path
        self.color = color

        # Flet Properties
        self.ref = ref
        self.col = col
        self.alignment = ft.alignment.center
        self.bgcolor = bgcolor
        self.border_radius = ft.border_radius.only(top_left=10, top_right=20, bottom_left=20, bottom_right=10)
        self.content = self.get_content()
        self.shadow = ft.BoxShadow(
            color=ft.colors.with_opacity(0.7, self.color),
            offset=ft.Offset(-5, 5),
            blur_style=ft.ShadowBlurStyle.NORMAL,
        )

    def get_content(self):
        print("@@@@@@@@@", self.ref)
        return ft.ListTile(
            leading=ft.Icon(self.icon, color=self.color) if self.icon else ft.Image(src=self.img_path,
                                                                                    fit=ft.ImageFit.COVER) if self.img_path else None,
            title=ft.Text(self.title, size=20, weight=ft.FontWeight.BOLD, text_align="right", color=self.color),
            subtitle=ft.Text(self.subtitle, size=12, text_align="right", color=self.color)
        )

    def update(self):
        self.content = self.get_content()
        super().update()


class TaskCard(ft.Card):
    def __init__(self, top_text, name, mobile, geo_location, address, on_click=None, **kwargs):
        super().__init__(**kwargs)
        self.top_text, self.name, self.mobile, self.geo_location, self.address, self.on_click = top_text, name, mobile, geo_location, address, on_click
        self.variant = ft.CardVariant.OUTLINED
        self.elevation = 2
        self.content = self.get_content()
        self.color = ft.colors.WHITE

    def update(self):
        self.content = self.get_content()
        super().update()

    def get_content(self):
        return ft.Container(
            padding=5,
            content=ft.ResponsiveRow(
                spacing=0,
                run_spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(self.top_text, size=10, text_align="center",
                            weight=ft.FontWeight.BOLD, color=SECONDARY),
                    ft.IconButton(ft.icons.PHONE, padding=0, col=1.5, icon_color=PRIMARY, on_click=lambda e: self.page.launch_url(f"tel:{self.mobile}") if self.mobile else None),
                    ft.Text(self.name, size=12,
                            weight=ft.FontWeight.BOLD, col=10.5, color=PRIMARY_CONTAINER),
                    ft.IconButton(ft.icons.LOCATION_ON, padding=0, col=1.5, icon_color=PRIMARY, on_click=lambda e: self.page.launch_url({self.geo_location}) if self.mobile else None),
                    ft.Text(self.address, size=12,
                            font_family="Roboto", col=7.5, color=PRIMARY_CONTAINER),
                    ft.Row(controls=[
                        ft.IconButton(ft.icons.CHECK, padding=0, icon_color=ft.colors.GREEN,
                                      bgcolor=ft.colors.TRANSPARENT, on_click=self.on_click),
                        ft.IconButton(ft.icons.CANCEL, padding=0, icon_color=ft.colors.RED,
                                      bgcolor=ft.colors.TRANSPARENT, on_click=self.on_click),
                    ], col=3)
                ]
            )
        )


class TaskCardDetail(ft.Card):
    def __init__(self, top_text, status, name, address, date, count, data={}, on_click=None, show_button=True,
                 **kwargs):
        super().__init__(**kwargs)
        self.top_text, self.status, self.name, self.address, self.date, self.count, self.data, self.on_click, self.show_button = top_text, status, name, address, date, count, data, on_click, show_button
        # self.variant = ft.CardVariant.OUTLINED
        self.elevation = 2
        self.color = ft.colors.WHITE
        self.content = self.get_content()

    def update(self):
        self.content = self.get_content()
        super().update()

    def get_content(self):
        content = ft.Container(
            on_click=self.on_click,
            data=self.data,
            padding=5,
            content=ft.ResponsiveRow(
                spacing=0,
                run_spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(self.top_text, size=10, weight=ft.FontWeight.BOLD, color=SECONDARY),
                            ft.Container(
                                border_radius=20,
                                padding=ft.padding.only(left=20, right=20),
                                content=ft.Text(self.status, size=10, weight=ft.FontWeight.BOLD,
                                                color=SECONDARY_CONTAINER),
                                bgcolor=SECONDARY
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.IconButton(ft.icons.PHONE, padding=0, col=1.5, icon_color=PRIMARY),
                    ft.Text(self.name, size=12,
                            weight=ft.FontWeight.BOLD, col=10.5, color=TERTIARY),
                    ft.IconButton(ft.icons.LOCATION_ON, padding=0, col=1.5, icon_color=PRIMARY),
                    ft.Text(self.address, size=12, col=10.5, color=TERTIARY),
                    ft.Icon(ft.icons.DATE_RANGE, col=1.5, color=PRIMARY),
                    ft.Text(self.date, size=12, col=4.5, color=TERTIARY),
                    ft.Icon(ft.icons.DISCOUNT, col=1.5, color=PRIMARY),
                    ft.Text(f"{self.count} items", size=12, col=4.5, color=TERTIARY),

                ]
            )
        )
        if self.show_button:
            content.content.controls.append(
                ft.Container(
                    content=ft.Row(
                        scale=0.8,
                        controls=[
                            ft.ElevatedButton('Accept', icon=ft.icons.CHECK, bgcolor=ft.colors.GREEN,
                                              color=ft.colors.WHITE),
                            ft.ElevatedButton('Reject', icon=ft.icons.CANCEL, bgcolor=ft.colors.RED,
                                              color=ft.colors.WHITE),
                        ], alignment=ft.MainAxisAlignment.END),
                    padding=ft.padding.only(top=10)
                )
            )

        return content

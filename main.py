import json
import urllib.request
import urllib.error
import flet as ft
from templates import SampleRod, TaskCard, TaskCardDetail, UserError
from colors import PRIMARY, PRIMARY_CONTAINER, ON_PRIMARY_CONTAINER, SECONDARY, SECONDARY_CONTAINER, \
    ON_SECONDARY_CONTAINER, TERTIARY, TERTIARY_CONTAINER, ON_TERTIARY_CONTAINER, BACKGROUND, GREY_DARK, WHITE_CONTAINER, \
    GREY_CONTAINER, GREY_OUTLINE
from pyodoo_connect import Odoo


def navigation_bar_route_changes(e):
    index = e.data
    if index == '1':
        e.control.page.go('/to_accept')
    elif index == '2':
        e.control.page.go('/to_deliver')
    else:
        e.control.page.go('/')


def on_click_view_record(e):
    e.control.page.go(f'/view#{e.control.data}')


class LoginView(ft.View):
    def __init__(self, page, data={}):
        super().__init__()
        self.data = data
        self.page = page
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.route = '/login'
        self.bgcolor = BACKGROUND

        self.appbar = ft.AppBar(title=ft.Text("Login"), center_title=True, bgcolor=ft.colors.SURFACE_VARIANT,
                                actions=[ft.IconButton(ft.icons.NOTIFICATIONS)])
        self.bottom_appbar = ft.BottomAppBar(
            height=15,
            padding=0,
            content=ft.Container(
                padding=0,
                alignment=ft.alignment.bottom_center,
                content=ft.Text("Copyright © 2024 BytesRaw", size=7, color=ft.colors.GREY, text_align="center")
            )
        )

        self.login_button = ft.Ref[ft.ElevatedButton]()
        self.url = ft.Ref[ft.TextField]()
        self.database = ft.Ref[ft.TextField]()
        self.username = ft.Ref[ft.TextField]()
        self.password = ft.Ref[ft.TextField]()

        self.controls = [
            ft.Container(
                height=150,
                bgcolor=ft.colors.TRANSPARENT,
                image_src='layers.gif',
            ),
            ft.Container(
                content=ft.ResponsiveRow(
                    controls=[
                        ft.Container(
                            padding=10,
                            bgcolor=ft.colors.WHITE,
                            border_radius=20,
                            content=ft.TextField(
                                ref=self.url,
                                prefix_icon=ft.icons.WEB_ASSET,
                                label="URL",
                                label_style=ft.TextStyle(color=PRIMARY),
                                text_style=ft.TextStyle(color=PRIMARY),
                                border=ft.InputBorder.NONE
                            ),
                        ),
                        ft.Container(
                            padding=10,
                            bgcolor=ft.colors.WHITE,
                            border_radius=20,
                            visible=False,
                            content=ft.TextField(
                                read_only=True,
                                ref=self.database,
                                prefix_icon=ft.icons.LIBRARY_BOOKS,
                                label="Database",
                                label_style=ft.TextStyle(color=PRIMARY),
                                text_style=ft.TextStyle(color=PRIMARY),
                                border=ft.InputBorder.NONE,
                            ),
                        ),
                        ft.Container(
                            padding=10,
                            bgcolor=ft.colors.WHITE,
                            border_radius=20,
                            visible=False,
                            content=ft.TextField(
                                ref=self.username,
                                prefix_icon=ft.icons.PERSON,
                                label="Login",
                                label_style=ft.TextStyle(color=PRIMARY),
                                text_style=ft.TextStyle(color=PRIMARY),
                                border=ft.InputBorder.NONE,
                            ),
                        ),
                        ft.Container(
                            padding=10,
                            bgcolor=ft.colors.WHITE,
                            border_radius=20,
                            visible=False,
                            content=ft.TextField(
                                ref=self.password,
                                prefix_icon=ft.icons.SECURITY,
                                label="Password",
                                label_style=ft.TextStyle(color=PRIMARY),
                                text_style=ft.TextStyle(color=PRIMARY),
                                border=ft.InputBorder.NONE,
                                password=True,
                                can_reveal_password=True,
                            ),
                        ),
                    ]
                ),
                scale=0.9
            ),
            ft.Container(
                ref=self.login_button,
                alignment=ft.alignment.center,
                content=ft.ElevatedButton(text="Login", icon=ft.icons.LOGIN, icon_color=ft.colors.WHITE,
                                          color=ft.colors.WHITE, bgcolor=PRIMARY, height=40, on_click=self.login_to_app)
            )
        ]

    def on_select_db(self, e):
        self.page.close_bottom_sheet()
        self.database.current.value = e.control.data
        self.database.current.parent.visible = True
        self.database.current.parent.update()
        self.username.current.parent.visible = True
        self.username.current.parent.update()
        self.password.current.parent.visible = True
        self.password.current.parent.update()

    def login_to_app(self, e):
        self.login_button.current.content = ft.ElevatedButton(
            content=ft.ProgressRing(color=GREY_DARK, width=20, height=20), bgcolor=PRIMARY, height=40, disabled=True)
        self.login_button.current.update()
        if self.url.current.value == '':
            self.url.current.error_text = "URL is required!"
            self.url.current.update()
        elif self.database.current.value == '':
            self.url.current.error_text = ""
            self.url.current.update()
            headers = {
                'Content-Type': 'application/json'
            }
            data = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {},
                "id": 1
            }
            data = json.dumps(data).encode("utf-8")

            try:
                req = urllib.request.Request(self.url.current.value + '/web/database/list', data=data, headers=headers)
                with urllib.request.urlopen(req) as response:
                    if response.status == 200:
                        databases = json.load(response).get('result')
                        bottom_sheet = ft.CupertinoActionSheet(
                            title=ft.Text("Select Database", text_align="center"),
                            cancel=ft.CupertinoActionSheetAction(
                                content=ft.Text("Cancel"),
                                on_click=lambda e: self.page.close_bottom_sheet(),
                            ),
                            actions=[
                                ft.CupertinoActionSheetAction(
                                    content=ft.Text(db),
                                    data=db,
                                    on_click=self.on_select_db,
                                ) for db in databases
                            ],
                        )
                        self.page.show_bottom_sheet(
                            ft.CupertinoBottomSheet(bottom_sheet)
                        )
                    else:
                        UserError(self.page, f"Error : {response.status}")
            except Exception as e:
                UserError(self.page, f"Error : {e}")
        else:
            input_fields = [
                (self.username.current, "Login is required!"),
                (self.password.current, "Password is required!"),
            ]
            all_set = True
            for input_field, error_msg in input_fields:
                input_field.error_text = error_msg if input_field.value == '' else None
                input_field.update()
                if input_field.value == '':
                    all_set = False
            if all_set:
                odoo_cr = dict(url=self.url.current.value, db=self.database.current.value,
                               username=self.username.current.value, password=self.password.current.value)
                try:
                    odoo = Odoo(url=odoo_cr['url'], db=odoo_cr['db'], username=odoo_cr['username'],
                                password=odoo_cr['password'])
                    if odoo.uid:
                        self.page.client_storage.set("odoo", odoo_cr)
                        self.page.data.update({"odoo": odoo})
                        self.page.update()
                        self.page.go('main')
                except Exception as e:
                    UserError(self.page, "Authentication Error !")

        self.login_button.current.content = ft.ElevatedButton(text="Login", icon=ft.icons.LOGIN,
                                                              icon_color=ft.colors.WHITE, color=ft.colors.WHITE,
                                                              bgcolor=PRIMARY, height=40, on_click=self.login_to_app)
        self.login_button.current.update()


class FormView(ft.View):
    def __init__(self, page, data={}):
        super().__init__()
        self.padding = 0
        self.data = data
        self.page = page

        self.route = '/view'
        self.bgcolor = BACKGROUND
        self.spacing = 0

        self.appbar = ft.AppBar(title=ft.Text("WH/100/20/2021"), center_title=True,
                                bgcolor=ft.colors.SURFACE_VARIANT, actions=[ft.IconButton(ft.icons.NOTIFICATIONS)])
        self.bottom_appbar = ft.BottomAppBar(
            height=15,
            padding=0,
            content=ft.Container(
                padding=0,
                alignment=ft.alignment.bottom_center,
                content=ft.Text("Copyright © 2024 BytesRaw", size=7, color=ft.colors.GREY, text_align="center")
            )
        )

        self.controls = [
            ft.Container(
                padding=10,
                bgcolor=PRIMARY_CONTAINER,
                content=ft.ResponsiveRow(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.IconButton(ft.icons.PHONE, padding=0, col=1.5, icon_color=ON_PRIMARY_CONTAINER),
                        ft.Row(
                            spacing=0,
                            controls=[
                                ft.Text(self.data.get('name', 'Customer Name'), size=12,
                                        weight=ft.FontWeight.BOLD, color=ON_PRIMARY_CONTAINER),
                                ft.Container(
                                    width=60,
                                    alignment=ft.alignment.center,
                                    padding=3,
                                    border_radius=10,
                                    bgcolor=SECONDARY,
                                    content=ft.Text(self.data.get('name', 'ready').upper(), size=12,
                                                    weight=ft.FontWeight.BOLD, color=SECONDARY_CONTAINER,
                                                    text_align="center"),
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            col=10.5,
                        ),
                        ft.IconButton(ft.icons.LOCATION_ON, padding=0, col=1.5, icon_color=ON_PRIMARY_CONTAINER),
                        ft.Text(self.data.get('address', 'Ad asjdhasd jhsad jasd Name'), size=12, col=10.5,
                                color=ON_PRIMARY_CONTAINER),
                        ft.Icon(ft.icons.DATE_RANGE, col=1.5, color=ON_PRIMARY_CONTAINER),
                        ft.Text(self.data.get('date', '12:04:2023 10:20:11'), size=12, col=4.5,
                                color=ON_PRIMARY_CONTAINER),
                    ])
            ),
            ft.Container(
                padding=10,
                bgcolor=TERTIARY_CONTAINER,
                content=ft.ResponsiveRow(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.icons.DISCOUNT, col=1.5, color=ON_TERTIARY_CONTAINER),
                        ft.Text(f"{self.data.get('count', '25')} items", size=12, col=4.5, color=ON_TERTIARY_CONTAINER),
                    ]
                )
            ),
            ft.ListView(
                expand=True,
                padding=10,
                spacing=10,
                controls=[
                    ft.Container(
                        bgcolor=WHITE_CONTAINER,
                        border_radius=20,
                        content=ft.ListTile(
                            leading=ft.Image(src='qr-code.gif', fit=ft.ImageFit.COVER, width=60, height=60),
                            title=ft.Text("Product Name KHSD SDHF SDJASKJ ASDKJASD JNSAD ASDHJGASD HASD ASKJDHASD ",
                                          size=12, color=PRIMARY),
                            subtitle=ft.ResponsiveRow(
                                controls=[
                                    ft.TextField(
                                        label="Demand",
                                        value="10",
                                        read_only=True,
                                        border=ft.InputBorder.NONE,
                                        col=6,
                                    ),
                                    ft.Container(
                                        content=ft.TextField(
                                            label="Qty Done",
                                            value="10",
                                            border=ft.InputBorder.NONE,
                                            label_style=ft.TextStyle(color=GREY_DARK),
                                            text_style=ft.TextStyle(color=GREY_DARK),
                                        ),
                                        bgcolor=ft.colors.GREY_200,
                                        col=6,
                                        padding=ft.padding.only(left=20),
                                        border_radius=30,
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_AROUND
                            )
                        ),
                        # shadow=ft.BoxShadow(
                        #     spread_radius=1,
                        #     color=ft.colors.BLUE_GREY_300,
                        #     offset=ft.Offset(-2, 2),
                        #     blur_style=ft.ShadowBlurStyle.OUTER,
                        # )
                    ) for x in range(10)
                ]
            ),
            ft.FloatingActionButton(
                icon=ft.icons.DONE_ALL_SHARP, bgcolor=GREY_OUTLINE, foreground_color=GREY_CONTAINER
            )
        ]


class ToDeliver(ft.View):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.route = 'to_deliver'
        self.bgcolor = BACKGROUND
        self.scroll = ft.ScrollMode.AUTO
        self.appbar = ft.AppBar(title=ft.Text("Tasks to Deliver"), center_title=True,
                                bgcolor=ft.colors.SURFACE_VARIANT, actions=[ft.IconButton(ft.icons.NOTIFICATIONS)])
        self.bottom_appbar = ft.BottomAppBar(
            height=90,
            padding=0,
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.NavigationBar(
                        selected_index=2,
                        on_change=lambda e: navigation_bar_route_changes(e),
                        destinations=[
                            ft.NavigationDestination(icon=ft.icons.DASHBOARD_OUTLINED, selected_icon=ft.icons.DASHBOARD,
                                                     label="Dashboard"),
                            ft.NavigationDestination(icon=ft.icons.PLAYLIST_ADD_CHECK_CIRCLE_OUTLINED,
                                                     selected_icon=ft.icons.PLAYLIST_ADD_CHECK_CIRCLE,
                                                     label="To Accept", ),
                            ft.NavigationDestination(icon=ft.icons.TASK_OUTLINED, selected_icon=ft.icons.TASK,
                                                     label="To Do", ),
                        ]
                    ),
                    ft.Container(
                        padding=0,
                        alignment=ft.alignment.bottom_center,
                        content=ft.Text("Copyright © 2024 BytesRaw", size=7, color=ft.colors.GREY, text_align="center")
                    )
                ]
            )
        )

        self.controls = [
            TaskCardDetail(top_text="SO213445 - WH/100/20/2021", status="DONE", name="Customer Name",
                           address="Address Test JHDSF  JAST", date="21-3-2024 10:11:30",
                           count="5", on_click=on_click_view_record, show_button=False, data=f"{self.page.route}#{x}")
            for x in range(5)
        ]


class ToAccept(ft.View):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.route = '/to_accept'
        self.scroll = ft.ScrollMode.AUTO
        self.bgcolor = BACKGROUND
        self.appbar = ft.AppBar(title=ft.Text("Tasks to Accept"), center_title=True,
                                bgcolor=ft.colors.SURFACE_VARIANT, actions=[ft.IconButton(ft.icons.NOTIFICATIONS)])
        self.bottom_appbar = ft.BottomAppBar(
            height=90,
            padding=0,
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.NavigationBar(
                        selected_index=1,
                        on_change=lambda e: navigation_bar_route_changes(e),
                        destinations=[
                            ft.NavigationDestination(icon=ft.icons.DASHBOARD_OUTLINED, selected_icon=ft.icons.DASHBOARD,
                                                     label="Dashboard"),
                            ft.NavigationDestination(icon=ft.icons.PLAYLIST_ADD_CHECK_CIRCLE_OUTLINED,
                                                     selected_icon=ft.icons.PLAYLIST_ADD_CHECK_CIRCLE,
                                                     label="To Accept", ),
                            ft.NavigationDestination(icon=ft.icons.TASK_OUTLINED, selected_icon=ft.icons.TASK,
                                                     label="To Do", ),
                        ]
                    ),
                    ft.Container(
                        padding=0,
                        alignment=ft.alignment.bottom_center,
                        content=ft.Text("Copyright © 2024 BytesRaw", size=7, color=ft.colors.GREY, text_align="center")
                    )
                ]
            )
        )

        self.controls = [
            TaskCardDetail(top_text="SO213445 - WH/100/20/2021", status="READY", name="Customer Name",
                           address="Address Test JHDSF  JHDSF JHSDF SKD NEW TEST", date="12-10-2024 10:11:30",
                           count="24", on_click=on_click_view_record, data=f"{self.page.route}#{x}") for x in range(20)
        ]


class RootView(ft.View):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.padding = 0
        self.route = 'main'
        # self.scroll = ft.ScrollMode.AUTO
        self.bgcolor = BACKGROUND
        self.odoo = None

        self.chart = ft.BarChart(
            height=150,
            bgcolor=TERTIARY,
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
                    ft.ChartAxisLabel(value=0, label=ft.Text("Jan", color=TERTIARY_CONTAINER)),
                    ft.ChartAxisLabel(value=1, label=ft.Text("Feb", color=TERTIARY_CONTAINER)),
                    ft.ChartAxisLabel(value=2, label=ft.Text("Mar", color=TERTIARY_CONTAINER)),
                    ft.ChartAxisLabel(value=3, label=ft.Text("Apr", color=TERTIARY_CONTAINER)),
                    ft.ChartAxisLabel(value=4, label=ft.Text("May", color=TERTIARY_CONTAINER)),
                    ft.ChartAxisLabel(value=5, label=ft.Text("Jun", color=TERTIARY_CONTAINER)),
                ],
            ),
            on_chart_event=self.on_chart_event,
            interactive=True,
        )

        self.appbar = ft.AppBar(title=ft.Text("Dashboard"), center_title=True,
                                bgcolor=ft.colors.SURFACE_VARIANT, actions=[ft.IconButton(ft.icons.NOTIFICATIONS)])
        self.bottom_appbar = ft.BottomAppBar(
            height=90,
            padding=0,
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.NavigationBar(
                        selected_index=0,
                        on_change=lambda e: navigation_bar_route_changes(e),
                        destinations=[
                            ft.NavigationDestination(icon=ft.icons.DASHBOARD_OUTLINED, selected_icon=ft.icons.DASHBOARD,
                                                     label="Dashboard"),
                            ft.NavigationDestination(icon=ft.icons.PLAYLIST_ADD_CHECK_CIRCLE_OUTLINED,
                                                     selected_icon=ft.icons.PLAYLIST_ADD_CHECK_CIRCLE,
                                                     label="To Accept", ),
                            ft.NavigationDestination(icon=ft.icons.TASK_OUTLINED, selected_icon=ft.icons.TASK,
                                                     label="To Do", ),
                        ]
                    ),
                    ft.Container(
                        padding=0,
                        alignment=ft.alignment.bottom_center,
                        content=ft.Text("Copyright © 2024 BytesRaw", size=7, color=ft.colors.GREY, text_align="center")
                    )
                ]
            )
        )
        self.summary_cards = {
            'New': ft.Ref[ft.Container](),
            'Accepted': ft.Ref[ft.Container](),
            'Delivered': ft.Ref[ft.Container](),
            'Cancelled': ft.Ref[ft.Container](),
        }
        self.controls = [
            ft.ResponsiveRow(
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                controls=[
                    ft.Container(
                        margin=ft.margin.all(5),
                        border_radius=20,
                        bgcolor=TERTIARY,
                        padding=10,
                        height=150,
                        content=self.chart
                    ),
                    ft.Container(
                        padding=ft.padding.only(left=20),
                        content=ft.Text("Total Tasks", size=18, color=PRIMARY)
                    ),
                    ft.Container(
                        col=5.5,
                        content=ft.ListTile(
                            leading=ft.Image(src='pending.gif', fit=ft.ImageFit.COVER),
                            title=ft.Text("", ref=self.summary_cards['New'], size=20, weight=ft.FontWeight.BOLD, text_align="right",
                                          color=PRIMARY),
                            subtitle=ft.Text("New", size=12, text_align="right", color=PRIMARY)
                        ),
                        border_radius=ft.border_radius.only(top_left=10, top_right=20, bottom_left=20,
                                                            bottom_right=10),
                        alignment=ft.alignment.center,
                        bgcolor=WHITE_CONTAINER,
                        shadow=ft.BoxShadow(
                            color=ft.colors.with_opacity(0.7, PRIMARY),
                            offset=ft.Offset(-5, 5),
                            blur_style=ft.ShadowBlurStyle.NORMAL,
                        )
                    ),
                    ft.Container(
                        col=5.5,
                        content=ft.ListTile(
                            leading=ft.Image(src='scheduled.gif', fit=ft.ImageFit.COVER),
                            title=ft.Text("", ref=self.summary_cards['Accepted'], size=20, weight=ft.FontWeight.BOLD, text_align="right",
                                          color=SECONDARY),
                            subtitle=ft.Text("Accepted", size=12, text_align="right", color=SECONDARY)
                        ),
                        border_radius=ft.border_radius.only(top_left=10, top_right=20, bottom_left=20,
                                                            bottom_right=10),
                        alignment=ft.alignment.center,
                        bgcolor=WHITE_CONTAINER,
                        shadow=ft.BoxShadow(
                            color=ft.colors.with_opacity(0.7, SECONDARY),
                            offset=ft.Offset(-5, 5),
                            blur_style=ft.ShadowBlurStyle.NORMAL,
                        )
                    ),
                    ft.Container(
                        col=5.5,
                        content=ft.ListTile(
                            leading=ft.Image(src='completed.gif', fit=ft.ImageFit.COVER),
                            title=ft.Text("", ref=self.summary_cards['Delivered'], size=20, weight=ft.FontWeight.BOLD, text_align="right",
                                          color=TERTIARY),
                            subtitle=ft.Text("Delivered", size=12, text_align="right", color=TERTIARY)
                        ),
                        border_radius=ft.border_radius.only(top_left=10, top_right=20, bottom_left=20,
                                                            bottom_right=10),
                        alignment=ft.alignment.center,
                        bgcolor=WHITE_CONTAINER,
                        shadow=ft.BoxShadow(
                            color=ft.colors.with_opacity(0.7, TERTIARY),
                            offset=ft.Offset(-5, 5),
                            blur_style=ft.ShadowBlurStyle.NORMAL,
                        )
                    ),
                    ft.Container(
                        col=5.5,
                        content=ft.ListTile(
                            leading=ft.Image(src='cancel.gif', fit=ft.ImageFit.COVER),
                            title=ft.Text("", ref=self.summary_cards['Cancelled'], size=20, weight=ft.FontWeight.BOLD, text_align="right",
                                          color=GREY_DARK),
                            subtitle=ft.Text("Cancelled", size=12, text_align="right", color=GREY_DARK)
                        ),
                        border_radius=ft.border_radius.only(top_left=10, top_right=20, bottom_left=20,
                                                            bottom_right=10),
                        alignment=ft.alignment.center,
                        bgcolor=WHITE_CONTAINER,
                        shadow=ft.BoxShadow(
                            color=ft.colors.with_opacity(0.7, GREY_DARK),
                            offset=ft.Offset(-5, 5),
                            blur_style=ft.ShadowBlurStyle.NORMAL,
                        )
                    ),
                    ft.Container(
                        padding=ft.padding.only(left=20),
                        content=ft.Text("Recent Tasks", size=18, color=PRIMARY)
                    )
                ]),
            ft.ListView(
                spacing=0,
                expand=True,
                padding=5,
                controls=[]
            ),
        ]
        self.page.run_thread(self.process_data)

    def process_data(self):
        if not self.page.data.get('odoo', False):
            odoo_cr = self.page.client_storage.get("odoo")
            try:
                self.odoo = Odoo(odoo_cr['url'], odoo_cr['db'], odoo_cr['username'], odoo_cr['password'])
                if self.odoo.uid:
                    self.page.data['odoo'] = self.odoo
                    self.page.update()
            except Exception as e:
                print(e)
                # UserError(self.page, e)
        self.odoo = self.page.data.get('odoo')
        stock = self.odoo.env['stock.picking'].browse(1)
        counts_data = stock.get_counts()
        print(counts_data)
        for name, ref in self.summary_cards.items():
            ref.current.value = counts_data[name]
            ref.current.update()
        tasks = stock.get_tasks(args={'status': "New", 'limit': 5})
        for task in tasks:
            self.controls[-1].controls.append(
                TaskCard(top_text=task.get('name', ''), name=task.get('partner_id', ''), mobile=task.get('mobile', ''), geo_location=task.get('geo_location', ''), address=task.get('address', ''),
                         on_click=self.on_click_accept_reject)
            )
            self.update()

    def on_click_accept_reject(self, e):
        print(self.page.data)

    def on_chart_event(self, e: ft.BarChartEvent):
        for group_index, group in enumerate(self.chart.bar_groups):
            for rod_index, rod in enumerate(group.bar_rods):
                rod.hovered = e.group_index == group_index and e.rod_index == rod_index
        self.chart.update()


def main(page: ft.Page):
    page.title = "Odoo Delivery App"
    page.theme_mode = ft.ThemeMode.LIGHT

    # page.fonts = {
    #     "AppFont": "OpenSans-VariableFont_wdth,wght.ttf"
    # }
    # page.theme = ft.theme.Theme(font_family="AppFont")

    def route_change(e):
        page.views.clear()
        if page.route == '/login':
            page.views.append(LoginView(page))
        else:
            page.views.append(
                RootView(page)
            )
            if page.route == "/to_accept":
                page.views.append(
                    ToAccept(page)
                )
            elif page.route == "/to_deliver":
                page.views.append(
                    ToDeliver(page)
                )
            elif '#' in page.route:
                route_data = page.route.split('#')
                back_route = route_data[-2]
                if back_route == "/to_accept":
                    page.views.append(
                        ToAccept(page)
                    )
                elif back_route == "/to_deliver":
                    page.views.append(
                        ToDeliver(page)
                    )
                data = {'id': route_data[-1]}
                page.views.append(
                    FormView(page, data=data)
                )
        page.update()

    def view_pop(e):
        print("Before pop", [x.route for x in page.views])
        page.views.pop()
        print("After pop", [x.route for x in page.views])
        page.update()
        # top_view = page.views[-1]
        # page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.route = 'main'

    if not page.data:
        page.data = {}
    if not page.client_storage.get("odoo"):
        page.route = '/login'

    page.go(page.route)


ft.app(main, assets_dir='assets')

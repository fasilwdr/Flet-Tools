import json
import urllib.request
import urllib.error
import flet as ft
from templates import SampleRod, TaskCard, TaskCardDetail, UserError, UserInfo, UserWarningg
from colors import PRIMARY, PRIMARY_CONTAINER, ON_PRIMARY_CONTAINER, SECONDARY, SECONDARY_CONTAINER, \
    ON_SECONDARY_CONTAINER, TERTIARY, TERTIARY_CONTAINER, ON_TERTIARY_CONTAINER, BACKGROUND, GREY_DARK, WHITE_CONTAINER, \
    GREY_CONTAINER, GREY_OUTLINE
from pyodoo_connect import Odoo
import re

app_version = "v0.1.4"
bytesraw_label = f"Copyright © 2024 BytesRaw            {app_version}"

PICKING_STATES = {
    'draft': 'Draft',
    'waiting': 'Waiting Another Operation',
    'confirmed': 'Waiting',
    'assigned': 'Ready',
    'done': 'Done',
    'cancel': 'Cancelled'
}
PICKING_PRIORITY = {
    '0': ft.icons.STAR_BORDER,
    '1': ft.icons.STAR,
}

WIZARD_CONTENT = {
    'confirm.stock.sms': "You are about to confirm this Delivery Order by SMS Text Message.",
    'stock.backorder.confirmation': "You have processed less products than the initial demand.\nCreate a backorder if you expect to process the remaining products later. Do not create a backorder if you will not process the remaining products."
}


def navigation_bar_route_changes(e):
    index = e.data
    if index == '1':
        e.control.page.go('main/to_accept')
    elif index == '2':
        e.control.page.go('main/to_deliver')
    else:
        e.control.page.go('main')


def on_click_view_record(e):
    e.control.page.go(f"main/{e.control.data['route']}/#{e.control.data['id']}")


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
                bgcolor="#E9EFF7",
                content=ft.Text(bytesraw_label, size=7, color=GREY_OUTLINE, text_align="center")
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
                        self.page.data.update({"odoo": odoo, "uid": odoo.uid})
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

        self.route = 'view'
        self.bgcolor = BACKGROUND
        self.spacing = 0
        record = execute_query(
            f"select partner_mobile, partner_name, state, geo_location_url, partner_address, scheduled_date, origin, delivery_note, name from stock_picking where odoo_id = {self.data.get('id')}"
        )
        self.appbar = ft.AppBar(title=ft.Text(record[0][-1]), center_title=True,
                                bgcolor=ft.colors.SURFACE_VARIANT, actions=[ft.IconButton(ft.icons.NOTIFICATIONS)])
        self.bottom_appbar = ft.BottomAppBar(
            height=15,
            padding=0,
            content=ft.Container(
                padding=0,
                alignment=ft.alignment.bottom_center,
                bgcolor="#E9EFF7",
                content=ft.Text(bytesraw_label, size=7, color=GREY_OUTLINE, text_align="center")
            )
        )
        self.odoo = self.page.data.get("odoo")
        count = execute_query(f"select count(*) from stock_move where picking_id = {self.data.get('id')}")[0][0]
        lines = execute_query(f"select * from stock_move where picking_id = {self.data.get('id')}")
        self.controls = [
            ft.Container(
                padding=10,
                bgcolor=PRIMARY_CONTAINER,
                content=ft.ResponsiveRow(
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.IconButton(ft.icons.PHONE, on_click=lambda e: self.page.launch_url(record[0][0]), padding=0,
                                      col=1.5, icon_color=ON_PRIMARY_CONTAINER),
                        ft.Text(record[0][1], size=12,
                                weight=ft.FontWeight.BOLD, color=ON_PRIMARY_CONTAINER, col=8.5),
                        ft.Container(
                            width=60,
                            alignment=ft.alignment.center,
                            padding=3,
                            border_radius=10,
                            bgcolor=SECONDARY,
                            content=ft.Text(PICKING_STATES[record[0][2]], size=12,
                                            weight=ft.FontWeight.BOLD, color=SECONDARY_CONTAINER,
                                            text_align="center"),
                            col=2
                        ),
                        ft.IconButton(ft.icons.LOCATION_ON, on_click=lambda e: self.page.launch_url(record[0][3]),
                                      padding=0, col=1.5, icon_color=ON_PRIMARY_CONTAINER),
                        ft.Text(record[0][4], size=12, col=10.5,
                                color=ON_PRIMARY_CONTAINER),
                        ft.Icon(ft.icons.DATE_RANGE, col=1.5, color=ON_PRIMARY_CONTAINER),
                        ft.Text(record[0][5], size=12, col=10.5,
                                color=ON_PRIMARY_CONTAINER),
                        ft.Icon(ft.icons.BOOK, col=1.5, color=ON_PRIMARY_CONTAINER),
                        ft.Text(record[0][6], size=12, col=10.5,
                                color=ON_PRIMARY_CONTAINER),
                        ft.Icon(ft.icons.NOTES, col=1.5, color=ON_PRIMARY_CONTAINER),
                        ft.Text(record[0][7], size=12, col=10.5,
                                color=ON_PRIMARY_CONTAINER),
                    ])
            ),
            ft.Container(
                padding=10,
                bgcolor=TERTIARY_CONTAINER,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(ft.icons.DISCOUNT, color=ON_TERTIARY_CONTAINER),
                        ft.Text(f"{count} items", size=12, color=ON_TERTIARY_CONTAINER),
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
                            leading=ft.Image(src='img.png' if not line[7] else None,
                                             src_base64=line[7] if line[7] else None, fit=ft.ImageFit.COVER, width=60,
                                             height=60),
                            title=ft.Text(line[3],
                                          size=12, color=PRIMARY),
                            subtitle=ft.ResponsiveRow(
                                controls=[
                                    ft.TextField(
                                        label="Demand",
                                        value=line[4] or 0.0,
                                        read_only=True,
                                        border=ft.InputBorder.NONE,
                                        col=6,
                                    ),
                                    ft.Container(
                                        content=ft.TextField(
                                            label="Qty Done",
                                            value=line[6] or line[4],
                                            input_filter=ft.InputFilter(regex_string=r"[0-9.]"),
                                            keyboard_type=ft.KeyboardType.NUMBER,
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
                        data=line[1]
                        # shadow=ft.BoxShadow(
                        #     spread_radius=1,
                        #     color=ft.colors.BLUE_GREY_300,
                        #     offset=ft.Offset(-2, 2),
                        #     blur_style=ft.ShadowBlurStyle.OUTER,
                        # )
                    ) for line in lines
                ]
            ),
            ft.FloatingActionButton(
                bgcolor=ft.colors.RED, foreground_color=GREY_CONTAINER,
                width=100,
                visible='to_deliver' in self.page.route,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.IconButton(icon=ft.icons.DONE, on_click=self.on_validate, key="validate",
                                      data=int(self.data.get('id'))),
                        ft.IconButton(icon=ft.icons.CANCEL, on_click=self.on_validate, key="cancel",
                                      data=int(self.data.get('id'))),
                    ])
            ),
            ft.FloatingActionButton(
                bgcolor=GREY_OUTLINE, foreground_color=GREY_CONTAINER,
                width=100,
                visible='to_accept' in self.page.route,
                content=ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.IconButton(icon=ft.icons.DONE, on_click=self.on_click_accept_reject,
                                      data={"accept": int(self.data.get('id'))}),
                        ft.IconButton(icon=ft.icons.CANCEL, on_click=self.on_click_accept_reject,
                                      data={"reject": int(self.data.get('id'))}),
                    ])
            ),
        ]

    def on_validate(self, e):
        splash = ft.AlertDialog(
            modal=True,
            title=ft.Text("Loading", text_align="center"),
            content=ft.CupertinoActivityIndicator(color=ft.colors.RED, radius=20)
        )
        self.page.show_dialog(splash)
        if not self.odoo:
            self.odoo = self.page.data.get('odoo')

        record = self.odoo.env['stock.picking'].browse(e.control.data)
        if e.control.key == 'validate':
            lines = self.controls[2].controls
            for line in lines:
                id = line.data
                qty = line.content.subtitle.controls[-1].content.value
                line_id = self.odoo.env['stock.move'].browse(id)
                print(line_id)
                line_id.update({
                    'quantity': float(qty),
                })
                execute_query(f"UPDATE stock_move set quantity = '{qty}' where odoo_id = '{id}'")
                print(id, qty)
            validate = record.button_validate()
            execute_query(f"UPDATE stock_picking set state = 'done' where odoo_id = '{e.control.data}'")
            self.page.close_dialog()
            if isinstance(validate, bool):
                if validate:
                    return UserInfo(self.page, "Done !", )
                else:
                    return UserError(self.page, "Something happened !\nContact with administrator")
            elif isinstance(validate, dict):
                self.open_alert_wizard(record, validate)
        elif e.control.key == 'cancel':
            record.action_cancel()
            execute_query(f"UPDATE stock_picking set state = 'cancel' where odoo_id = '{e.control.data}'")
            return UserWarningg(self.page, "Task has been Cancelled !", )

    def open_alert_wizard(self, record, args):
        def return_action(e):
            self.page.close_dialog()
            res = record.return_action(args={'res': args, 'method': e.control.data})
            if isinstance(res, bool):
                if res:
                    return UserInfo(self.page, "Done !", )
                else:
                    return UserError(self.page, "Something happened !\nContact with administrator")
            elif isinstance(res, dict):
                self.open_alert_wizard(record, res)

        name = args.get('name')
        res_model = args.get('res_model')
        wizard = ft.AlertDialog(
            modal=True,
            title=ft.Text(name),
            content=ft.Text(WIZARD_CONTENT[res_model]),
            actions=[
                ft.TextButton("Confirm", on_click=return_action, data='send_sms',
                              visible=res_model in ['confirm.stock.sms']),
                ft.TextButton("Disable SMS", on_click=return_action, data='dont_send_sms',
                              visible=res_model in ['confirm.stock.sms']),
                ft.TextButton("Create Backorder", on_click=return_action, data='process',
                              visible=res_model in ['stock.backorder.confirmation']),
                ft.TextButton("No Backorder", on_click=return_action, data='process_cancel_backorder',
                              visible=res_model in ['stock.backorder.confirmation']),
                ft.TextButton("Cancel", on_click=lambda e: self.page.close_dialog()),
            ]
        )
        self.page.show_dialog(wizard)

    def on_click_accept_reject(self, e):
        action = e.control.data
        vals = "accept" if "accept" in action else "reject"
        try:
            if not self.odoo:
                self.odoo = self.page.data.get("odoo")
            picking_id = self.odoo.env['stock.picking'].browse(action[vals])
            picking_id.delivery_accept = vals
            execute_query(f"UPDATE stock_picking set delivery_accept = '{vals}' where odoo_id = '{action[vals]}'")
            f_button = e.control.parent.parent
            f_button.visible = False
            f_button.update()
        except Exception as e:
            return UserError(self.page, e)
        UserInfo(self.page, "Task accepted")
        self.update()


class Tasks(ft.View):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.route = 'tasks'
        self.scroll = ft.ScrollMode.AUTO
        self.bgcolor = BACKGROUND
        self.appbar = ft.AppBar(title=ft.Text("Tasks to Accept" if 'to_accept' in self.page.route else "Tasks to Deliver"), center_title=True,
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
                            ft.NavigationBarDestination(icon=ft.icons.DASHBOARD_OUTLINED,
                                                        selected_icon=ft.icons.DASHBOARD,
                                                        label="Dashboard"),
                            ft.NavigationBarDestination(icon=ft.icons.PLAYLIST_ADD_CHECK_CIRCLE_OUTLINED,
                                                        selected_icon=ft.icons.PLAYLIST_ADD_CHECK_CIRCLE,
                                                        label="To Accept", ),
                            ft.NavigationBarDestination(icon=ft.icons.TASK_OUTLINED, selected_icon=ft.icons.TASK,
                                                        label="To Do", ),
                        ]
                    ),
                    ft.Container(
                        padding=0,
                        alignment=ft.alignment.bottom_center,
                        bgcolor="#E9EFF7",
                        content=ft.Text(bytesraw_label, size=7, color=GREY_OUTLINE, text_align="center")
                    )
                ]
            )
        )
        self.controls = [
            ft.Container(
                alignment=ft.alignment.center,
                padding=10,
                content=ft.CupertinoActivityIndicator(radius=20, color=PRIMARY_CONTAINER)
            )
        ]
        self.odoo = self.page.data.get("odoo")
        print(self.odoo)
        if not self.odoo:
            self.page.run_thread(self.get_odoo)
        self.stock_picking = None
        self.page.run_thread(self.get_stock_picking)
        self.page.run_thread(self.get_task_controls)

    def get_stock_picking(self):
        while True:
            if self.odoo:
                print("get_stock_picking")
                self.stock_picking = self.odoo.env['stock.picking'].browse(1)
                if self.stock_picking:
                    break
            if self.page.route != self.route:
                break

    def get_odoo(self):
        try:
            odoo_cr = self.page.client_storage.get("odoo")
            self.odoo = Odoo(odoo_cr['url'], odoo_cr['db'], odoo_cr['username'], odoo_cr['password'])
            if self.odoo.uid:
                self.page.data['uid'] = self.odoo.uid
                self.page.data['odoo'] = self.odoo
                self.page.update()
        except Exception as e:
            if self.page:
                UserError(self.page, e)

    def get_task_controls(self):
        while True:
            if self.stock_picking:
                print("Got stock picking")
                task_data = self.stock_picking.get_tasks(args={'status': 'New'})
                tasks = []
                for task in task_data:
                    tasks.append(
                        TaskCardDetail(
                            top_text=f"{task.get('origin')} - {task.get('name')}" if task.get('origin') else task.get(
                                'name'), status=PICKING_STATES[task.get('state')], name=task.get('partner_name'),
                            address=task.get('partner_address'), date=task.get('scheduled_date'),
                            count=len(task.get('move_ids_without_package')),
                            on_click=on_click_view_record, data={'id': task.get('odoo_id'), 'route': self.page.route},
                            on_accept_reject=self.on_click_accept_reject if 'to_accept' in self.page.route else None,

                    ))
                if not tasks:
                    tasks.append(ft.Card(
                        elevation=2,
                        height=100,
                        color=ft.colors.WHITE,
                        content=ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.Icon(ft.icons.HOURGLASS_EMPTY),
                                ft.Text("No Tasks")
                            ]
                        )
                    ))
                self.controls.clear()
                self.controls.extend(tasks)
                self.update()
                print("Updated")
                break
            if self.page.route != self.route:
                break

    def on_click_accept_reject(self, e):
        action = e.control.data
        vals = "accept" if "accept" in action else "reject"
        try:
            if not self.odoo:
                self.odoo = self.page.data.get("odoo")
            picking_id = self.odoo.env['stock.picking'].browse(action[vals])
            picking_id.delivery_accept = vals
            card = e.control.parent.parent.parent.parent.parent
            for control in self.controls:
                if control == card:
                    self.controls.remove(control)
        except Exception as e:
            return UserError(self.page, e)
        UserInfo(self.page, "Task accepted" if 'to_accept' in self.page.route else "Done !")
        if not self.controls:
            self.controls.append(
                ft.Card(
                    elevation=2,
                    height=100,
                    color=ft.colors.WHITE,
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.icons.HOURGLASS_EMPTY),
                            ft.Text("No Tasks")
                        ]
                    )
                )
            )
        self.update()


class RootView(ft.View):
    def __init__(self, page):
        super().__init__()
        self.page = page
        self.padding = 0
        self.route = 'main'
        # self.scroll = ft.ScrollMode.AUTO
        self.bgcolor = BACKGROUND
        self.odoo = self.page.data.get('odoo')
        if not self.odoo:
            self.page.run_thread(self.get_odoo)
        self.stock_picking = None
        self.page.run_thread(self.get_stock_picking)
        self.chart = ft.Ref[ft.Container]()

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
                            ft.NavigationBarDestination(icon=ft.icons.DASHBOARD_OUTLINED,
                                                        selected_icon=ft.icons.DASHBOARD,
                                                        label="Dashboard"),
                            ft.NavigationBarDestination(icon=ft.icons.PLAYLIST_ADD_CHECK_CIRCLE_OUTLINED,
                                                        selected_icon=ft.icons.PLAYLIST_ADD_CHECK_CIRCLE,
                                                        label="To Accept", ),
                            ft.NavigationBarDestination(icon=ft.icons.TASK_OUTLINED, selected_icon=ft.icons.TASK,
                                                        label="To Do", ),
                        ]
                    ),
                    ft.Container(
                        padding=0,
                        alignment=ft.alignment.bottom_center,
                        bgcolor="#E9EFF7",
                        content=ft.Text(bytesraw_label, size=7, color=GREY_OUTLINE, text_align="center")
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
        self.list_view = ft.Ref[ft.ListView]()
        self.controls = [
            ft.ResponsiveRow(
                alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                controls=[
                    ft.Container(
                        ref=self.chart,
                        margin=ft.margin.all(5),
                        border_radius=20,
                        bgcolor=TERTIARY,
                        padding=10,
                        height=150,
                        content=ft.Container(
                            alignment=ft.alignment.center,
                            padding=10,
                            content=ft.CupertinoActivityIndicator(radius=20, color=SECONDARY_CONTAINER)
                        )
                    ),
                    ft.Container(
                        padding=ft.padding.only(left=20),
                        content=ft.Text("Total Tasks", size=18, color=PRIMARY)
                    ),
                    ft.Container(
                        col=5.5,
                        content=ft.ListTile(
                            leading=ft.Image(src='pending.gif', fit=ft.ImageFit.COVER),
                            ref=self.summary_cards["New"],
                            title=ft.Text("", size=20, weight=ft.FontWeight.BOLD, text_align="right", color=PRIMARY),
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
                            ref=self.summary_cards["Accepted"],
                            title=ft.Text("", size=20, weight=ft.FontWeight.BOLD, text_align="right", color=SECONDARY),
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
                            ref=self.summary_cards["Delivered"],
                            title=ft.Text("", size=20, weight=ft.FontWeight.BOLD, text_align="right", color=TERTIARY),
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
                            ref=self.summary_cards["Cancelled"],
                            title=ft.Text("", size=20, weight=ft.FontWeight.BOLD, text_align="right", color=GREY_DARK),
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
                ref=self.list_view,
                spacing=0,
                expand=True,
                padding=5,
                controls=[ft.Container(
                    alignment=ft.alignment.center,
                    padding=10,
                    content=ft.CupertinoActivityIndicator(radius=15, color=PRIMARY)
                )]
            ),
        ]
        self.page.run_thread(self.build_chart)
        self.page.run_thread(self.build_count)
        self.page.run_thread(self.build_tasks)

    def get_odoo(self):
        try:
            odoo_cr = self.page.client_storage.get("odoo")
            self.odoo = Odoo(odoo_cr['url'], odoo_cr['db'], odoo_cr['username'], odoo_cr['password'])
            if self.odoo.uid:
                self.page.data['uid'] = self.odoo.uid
                self.page.data['odoo'] = self.odoo
                self.page.update()
        except Exception as e:
            if self.page:
                UserError(self.page, e)

    def get_stock_picking(self):
        while True:
            if self.odoo:
                self.stock_picking = self.odoo.env['stock.picking'].browse(1)
                if self.stock_picking:
                    break
            if self.page.route != self.route:
                break

    def build_count(self):
        while True:
            if self.stock_picking:
                task_count = self.stock_picking.get_counts()
                for key, ref in self.summary_cards.items():
                    ref.current.title.value = task_count[key]
                    ref.current.update()
                break
            if self.page.route != self.route:
                break

    def build_tasks(self):
        while True:
            if self.stock_picking:
                task_data = self.stock_picking.get_tasks(args={'status': 'New'})
                tasks = []
                for task in task_data:
                    tasks.append(TaskCard(
                        top_text=f"{task.get('origin')} - {task.get('name')}" if task.get('origin') else task.get(
                            'name'), name=task.get('partner_name'), mobile=task.get('partner_mobile'),
                        geo_location=task.get('geo_location_url'), address=task.get('partner_address'),
                        on_click=self.on_click_accept_reject, data_id=task.get('odoo_id'), data=task))
                if tasks:
                    self.list_view.current.controls.clear()
                    self.list_view.current.controls.extend(tasks)
                    self.list_view.current.update()
                break
            if self.page.route != self.route:
                break

    def build_chart(self):
        while True:
            if self.stock_picking:
                chart_data = self.stock_picking.get_chart_data()
                chart = ft.BarChart(
                    height=150,
                    bgcolor=TERTIARY,
                    bar_groups=[
                        ft.BarChartGroup(
                            x=0,
                            bar_rods=[SampleRod(cd.get('count'))],
                        ) for cd in chart_data
                    ],
                    bottom_axis=ft.ChartAxis(
                        labels=[
                            ft.ChartAxisLabel(value=0, label=ft.Text(cd.get('month'), color=TERTIARY_CONTAINER)) for cd
                            in
                            chart_data
                        ],
                    ),
                    on_chart_event=self.on_chart_event,
                    interactive=True,
                )
                self.chart.current.content = chart
                self.chart.current.update()
                break
            if self.page.route != self.route:
                break

    def on_click_accept_reject(self, e):
        action = e.control.data
        vals = "accept" if "accept" in action else "reject"
        print(action, vals)
        try:
            if self.odoo:
                picking_id = self.odoo.env['stock.picking'].browse(action[vals])
                picking_id.delivery_accept = vals
                print(picking_id.delivery_accept)
            card = e.control.parent.parent.parent.parent
            for control in self.controls[-1].controls:
                if control == card:
                    self.controls[-1].controls.remove(control)
        except Exception as e:
            return UserError(self.page, e)
        self.update()
        UserInfo(self.page, "Task accepted")

    def on_chart_event(self, e: ft.BarChartEvent):
        for group_index, group in enumerate(self.chart.current.content.bar_groups):
            for rod_index, rod in enumerate(group.bar_rods):
                rod.hovered = e.group_index == group_index and e.rod_index == rod_index
        self.chart.current.update()


def main(page: ft.Page):
    page.title = "Odoo Delivery App"
    page.theme_mode = ft.ThemeMode.LIGHT

    # page.fonts = {
    #     "AppFont": "OpenSans-VariableFont_wdth,wght.ttf"
    # }
    # page.theme = ft.theme.Theme(font_family="AppFont")

    def route_change(e):
        print("page.route", page.route)
        # page.views.clear()
        if page.route == '/login':
            page.views.clear()
            page.views.append(LoginView(page))
        elif page.route == 'main':
            page.views.clear()
            page.views.append(RootView(page))
        else:
            view = page.route.split('/')
            current_view = view[-1]
            if current_view in ["to_accept", "to_deliver"]:
                page.views.append(
                    Tasks(page)
                )
            # if '#' in page.route:
            #     match = re.search(r"#(\d+)", page.route)
            #     data = {'id': match.group(1) if match else None}
            #     page.views.append(
            #         FormView(page, data=data)
            #     )
        page.update()

    def view_pop(e):
        route = page.route.split("/")
        if len(route) > 1:
            route.pop()
            page.route = '/'.join(route)
        page.views.pop()
        page.update()

    def page_on_error(e):
        alert = ft.AlertDialog(
            modal=True,
            title=ft.Text("Error !!", color=ft.colors.RED),
            content=ft.ListView(
                expand=True,
                controls=[
                    ft.Text(e.data)
                ]
            ),
            actions=[
                ft.TextButton("Ok", on_click=lambda e: page.close_dialog())
            ],
            actions_alignment=ft.MainAxisAlignment.END, )
        page.show_dialog(alert)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.on_error = page_on_error
    page.route = 'main'
    if not page.data:
        page.data = {}
    if not page.client_storage.get("odoo"):
        page.route = '/login'

    page.go(page.route)


ft.app(main, assets_dir='assets')

import flet as ft
import json
import os
from typing import Optional, Callable

from pages import home_page, riot_page, bnet_page, settings_page
from custom_controls import custom_text_button, custom_icon_button
from custom_controls import resource_path
from wizard import wizard
from profiles_edit import profiles_edit
import riot_logic
from third_party_apps import THIRD_PARTY_APPS

# ----------------- End of imports -----------------

HEXTECK_GOLD = "#D4AF37"
BLOOD_RED = "#AD0000"

class AppState:
    def __init__(self):
        self.is_switching = False
        self.update_ticker: Optional[Callable] = None
        self.curret_service = None

        self.helper_options = {app["display"]: key for key, app in THIRD_PARTY_APPS.items()}
        self.selected_helper_display = "Porofessor (Standalone)"
        
        self.config_path = os.path.join(riot_logic.RIOVERT_DIR, "riovert_config.json")
        self.load_config()

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r") as f:
                    data = json.load(f)
                    if data.get("selected_helper") in self.helper_options:
                        self.selected_helper_display = data["selected_helper"]
            except Exception:
                pass

    def save_config(self):
        try:
            with open(self.config_path, "w") as f:
                json.dump({"selected_helper": self.selected_helper_display}, f)
        except Exception:
            pass

def main(page: ft.Page):

    page.title = "Riovert"
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0
    page.bgcolor = ft.Colors.TRANSPARENT
    page.window.icon = resource_path("assets/Riovert.ico")
    page.window.width = 1450
    page.window.height = 800
    page.window.alignment = ft.Alignment.CENTER
    page.window.title_bar_hidden = True
    page.window.frameless = True
    page.window.bgcolor = ft.Colors.TRANSPARENT

    def minimize_window():
        page.window.minimized = True
        page.update()

    async def close_window():
        await page.window.close()
    
    def handle_maximize():
        page.window.maximized = not page.window.maximized
        page.update()

    custom_titlebar = ft.WindowDragArea(
        content=ft.Container(
            height=35,
            margin=ft.Margin.all(0),
            padding=ft.Padding.only(left=8, right=10, top=2, bottom=2),
            bgcolor=ft.Colors.with_opacity(0.8, "#1F1F1F"), # Dark, slightly transparent
            border=ft.Border.only(bottom=ft.BorderSide(1, ft.Colors.with_opacity(0.5, HEXTECK_GOLD))),
            content=ft.Row(
                margin=ft.Margin.all(0),
                spacing=0,
                controls=[
                    # Left Side: App Name and Icon
                    ft.Row(
                        controls=[
                            ft.Image(src=resource_path("assets/Riovert.ico")),
                            ft.Text("RIOVERT", color=HEXTECK_GOLD, weight=ft.FontWeight.BOLD, size=12, font_family="Consolas")
                        ],
                        spacing=10
                    ),
                    # Right Side: Window Controls
                    ft.Row(
                        controls=[
                            custom_icon_button(minimize_window, icon=ft.Icons.CIRCLE, icon_color="#FFBD44", animate_hover_color=True),
                            custom_icon_button(handle_maximize, icon=ft.Icons.CIRCLE, icon_color="#00CA4E", animate_hover_color=True),
                            custom_icon_button(close_window, icon=ft.Icons.CIRCLE, icon_color="#FF605C", animate_hover_color=True)
                        ],
                        spacing=0
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )
    )

    state = AppState()

    status_text = ft.Text("> [SYSTEM] IDLE", color=HEXTECK_GOLD, weight=ft.FontWeight.BOLD, size=18)

    def update_ticker(msg):
        status_text.value = f"> {msg.upper()}"
        page.update()

    state.update_ticker = update_ticker

    async def kill_switch():
        
        update_ticker("[SYSTEM] PURGING ALL GAME SERVICES...")

        await riot_logic.force_kill_all_services()
        await riot_logic.kill_helpers()

        update_ticker("[SYSTEM] PURGING COMPLETE.")

    bottom_bar = ft.Container(
        bgcolor=ft.Colors.with_opacity(0.1, "#8D8D8D"),
        blur=ft.Blur(30, 15, ft.BlurTileMode.CLAMP),
        border=ft.Border.only(top=ft.BorderSide(1, ft.Colors.with_opacity(0.1, HEXTECK_GOLD))),
        height=60,
        padding=ft.Padding.symmetric(horizontal=15),
        content=ft.Row(
            controls=[
                status_text,
                custom_text_button(lambda: page.run_task(kill_switch), text="TERMINATE ALL PROCESSES", width=250, active_color=BLOOD_RED)
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
    )

    def build_view_with_bb(route_url, content_block):
        view_controls: list[ft.BaseControl]=[
            # LAYER 1: The Master Container (Handles the Image)
            ft.Container(
                expand=True,
                margin=ft.Margin.all(0),
                padding=ft.Padding.all(0),
                image=ft.DecorationImage(
                    src=resource_path("assets/Red_Land_darker_bg.jpg"), 
                    fit=ft.BoxFit.FILL,
                ),
                # LAYER 2: The Gradient Dimmer Container
                content=ft.Column(
                    spacing=0,
                    margin=ft.Margin.all(0),
                    controls=[
                        custom_titlebar,
                        ft.Container(
                            expand=True,
                            gradient=ft.LinearGradient(
                                begin=ft.Alignment.TOP_CENTER,
                                end=ft.Alignment.BOTTOM_CENTER,
                                colors=[
                                    ft.Colors.with_opacity(0.3, "#000000"),
                                    ft.Colors.with_opacity(0.8, "#000000"), # Slightly darker at the bottom for the chin
                                ]
                            ),
                            # LAYER 3: The UI Column
                            content=ft.Column(
                                expand=True,
                                spacing=0,
                                controls=[
                                    ft.Container(content=content_block, expand=True),
                                    bottom_bar # <--- Sits beautifully over the background!
                                ]
                            )
                        )
                    ]
                )
            )
        ]

        return ft.View(
            route=route_url,
            padding=0,
            spacing=0,
            controls=view_controls
        )

    def build_view_no_bb(route_url, content_block):
        view_controls: list[ft.BaseControl]=[
            ft.Container(
                expand=True,
                margin=ft.Margin.all(0),
                padding=ft.Padding.all(0),
                image=ft.DecorationImage(
                    src=resource_path("assets/Red_Land_darker_bg.jpg"), 
                    fit=ft.BoxFit.FILL,
                ),
                content=ft.Column(
                    spacing=0,
                    margin=ft.Margin.all(0),
                    controls=[
                        custom_titlebar,
                        ft.Container(
                            expand=True,
                            margin=ft.Margin.all(0),
                            padding=ft.Padding.all(0),
                            gradient=ft.LinearGradient(
                                begin=ft.Alignment.TOP_CENTER,
                                end=ft.Alignment.BOTTOM_CENTER,
                                colors=[
                                    ft.Colors.with_opacity(0.3, "#000000"),
                                    ft.Colors.with_opacity(0.8, "#000000"),
                                ]
                            ),
                            content=ft.Container(content=content_block, expand=True, margin=ft.Margin.all(0), padding=ft.Padding.all(0))
                        )
                    ]
                )
            )
        ]

        return ft.View(
            route=route_url,
            padding=0,
            spacing=0,
            controls=view_controls
        )

    def route_change(e: ft.RouteChangeEvent):
        page.views.clear()
        
        if page.route == "/riot":
            page.views.append(build_view_with_bb("/riot", riot_page(page, state)))
        elif page.route == "/bnet":
            page.views.append(build_view_with_bb("/bnet", bnet_page(page, state)))
        elif page.route == "/settings":
            page.views.append(build_view_no_bb("/settings", settings_page(page)))
        elif page.route == "/wizard":
            page.views.append(build_view_no_bb("/wizard", wizard(page)))
        elif page.route.startswith("/edit/"):
            pid = page.route.split("/")[-1] 
            page.views.append(build_view_no_bb(page.route, profiles_edit(page, state, pid)))
        else:
            page.views.append(build_view_no_bb("/home", home_page(page)))
            
        page.update()
    page.on_route_change = route_change

    page.go("/home")

if __name__ == "__main__":
    ft.run(main)
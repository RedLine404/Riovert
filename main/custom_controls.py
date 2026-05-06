import flet as ft
import os
import sys

HEXTECK_GOLD = "#D4AF37"
BLOOD_RED = "#AD0000"

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller (.exe)"""
    # Safely checks for the PyInstaller folder without making VS Code angry!
    base_path = getattr(sys, '_MEIPASS', None)
    
    if not base_path:
        # We are running in Dev Mode, use the project root (one level up from this script's directory)
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    return os.path.join(base_path, relative_path)

def on_hover(e, change_color: bool, idle_color: str = ft.Colors.with_opacity(0.13, "#FFFFFF"), active_color: str = BLOOD_RED, change_size: bool = True, animate: bool = True):
        e.control.scale = 1.05 if change_size and e.data else 1.0
        e.control.bgcolor = active_color if change_color and e.data else idle_color
        e.control.animate = ft.Animation(300, ft.AnimationCurve.EASE_OUT) if animate else animate == False
        e.control.animate_scale = ft.Animation(200, ft.AnimationCurve.EASE_OUT_BACK) if animate else animate == False
        e.control.update()

def custom_text_button(action, text, width: int=110, height:int = 50, idle_color: str = ft.Colors.with_opacity(0.13, "#FFFFFF"), active_color: str = BLOOD_RED):
    return ft.Container(
        content=ft.Text(text, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD),
        bgcolor=idle_color,
        border=ft.Border.all(2, active_color),
        border_radius=12,
        alignment=ft.Alignment.CENTER,
        width=width,
        height=height,
        ink=True,
        on_click=action,
        on_hover=lambda e: on_hover(e, True, idle_color, active_color, True, True)
    )

def custom_icon_button(action, icon, width: int=30, height:int = 30, hover_color: str = ft.Colors.TRANSPARENT, icon_color: str = BLOOD_RED, animate_hover_color: bool = True, animate_size_change: bool = True):
    return ft.Container(
        content=ft.Icon(icon, color=icon_color),
        alignment=ft.Alignment.CENTER,
        bgcolor=ft.Colors.TRANSPARENT,
        width=width,
        height=height,
        ink=True,
        on_click=action,
        on_hover=lambda e: on_hover(e, change_color=True, idle_color=hover_color, active_color=ft.Colors.with_opacity(0.13, "#FFFFFF"), change_size=animate_size_change, animate=animate_hover_color)
    )


def sidebar(page: ft.Page):
    return ft.Container(
        width=80,
        bgcolor=ft.Colors.TRANSPARENT,
        border=ft.Border.only(right=ft.BorderSide(1, ft.Colors.with_opacity(0.3, HEXTECK_GOLD))),
        padding=ft.Padding.symmetric(vertical=20),
        margin=ft.Margin.only(bottom=10, top=10),
        content=ft.Column(
            controls=[
                ft.Column(
                    controls=[
                        ft.IconButton(
                            icon=ft.Icons.HOME,
                            icon_color=ft.Colors.WHITE,
                            icon_size=30,
                            bgcolor=ft.Colors.with_opacity(0.13, "#FFFFFF"),
                            on_hover=lambda e: on_hover(e, True, ft.Colors.with_opacity(0.13, "#FFFFFF"), BLOOD_RED, True, True),
                            on_click=lambda: page.go("/home")
                        ),
                        ft.Container(
                            width=15, height=15, border_radius=8,
                            bgcolor=ft.Colors.TRANSPARENT,
                            margin=ft.margin.only(top=20)
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                ),
                ft.IconButton(
                    icon=ft.Icons.SETTINGS, 
                    icon_color=HEXTECK_GOLD, # Hextech Gold
                    icon_size=30,
                    bgcolor=ft.Colors.with_opacity(0.13, "#FFFFFF"),
                    on_hover=lambda e: on_hover(e, True, ft.Colors.with_opacity(0.13, "#FFFFFF"), BLOOD_RED, True, True),
                    on_click=lambda: page.go("/settings")
                )
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
    )



def custom_card(page, title: str, image_path: str, target_page=None, action=None, idle_color: str = ft.Colors.with_opacity(0.13, "#FFFFFF"), active_color:str = BLOOD_RED):
    async def handle_on_click(e):
        if target_page:
            page.go(target_page)
            
        elif action:
            action()

    return ft.Container(
        width=300,
        height=500,
        border_radius=ft.BorderRadius.only(bottom_left=15, bottom_right=15),
        padding=ft.Padding.all(2),
        margin=ft.Margin.only(top=20, bottom=20),
        bgcolor=idle_color,
        ink=True,
        on_click=handle_on_click,
        on_hover = lambda e: on_hover(e, True, idle_color, active_color),
        content=ft.Column(
            controls=[
                ft.Image(src=resource_path(f"assets/{image_path}"), expand=True, fit=ft.BoxFit.COVER),
                ft.Text(title, size=18, weight=ft.FontWeight.BOLD, color="white")
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )
    )

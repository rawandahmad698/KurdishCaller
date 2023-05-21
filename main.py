import json
import flet as ft
import httpx

# IMPORTANT: Change this to your own token
auth_token = "YOUR_TOKEN_HERE"

async def get_number_info(number: str):
    headers = {
        'Host': 'search5-noneu.truecaller.com',
        'Connection': 'keep-alive',
        'Accept': '*/*',
        'User-Agent': 'Truecaller/12.38.7 (com.truesoftware.TrueCallerOther; build:12.38.7; iOS 16.0.3) Alamofire/5.5.0',
        'Accept-Language': 'en;q=1.0, ckb-US;q=0.9',
        'Authorization': f'Bearer {auth_token}',
    }

    params = {
        "countryCode": "iq",
        "q": number,
        "type": "4",
    }

    url = "https://search5-noneu.truecaller.com/v2/search"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        if response.status_code != 200:
            return None

        response_json = response.json()
        data = response_json["data"][0] if len(response_json["data"]) > 0 else None
        if data is None:
            return None

        if 'name' not in data:
            return None

        return {
            "name": data["name"],
            "score": data["score"],
        }


class KurdishCaller(ft.UserControl):
    def __init__(self):
        self.container = None
        self.ring = None
        self.results = None
        self.textfield = None

    def build(self):
        self.textfield = ft.TextField(hint_text="بە دوای ژمارەیەکدا بگەڕێ...", expand=True, )
        self.results = ft.Column()
        self.ring = ft.ProgressRing(visible=False)
        self.container = ft.Container(self.ring, alignment=ft.alignment.center, padding=5)

        return ft.Column(
            width=600,
            controls=[
                ft.Row(
                    controls=[
                        self.textfield,
                        ft.FloatingActionButton(icon=ft.icons.SEARCH, on_click=self.search)
                    ]
                ),
                self.container,
                self.results
            ]
        )

    async def search(self, sender):
        self.ring.visible = True
        await self.update_async()

        number = self.textfield.value
        number_info = await get_number_info(number)

        self.ring.visible = False
        await self.update_async()

        if number_info is None:
            self.results.controls = [ft.Text("هیچ زانیاریەک نەدۆزرایەوە")]
            await self.update_async()
            return

        score = number_info["score"]
        score = round(score, 2)
        score = score * 100
        score = round(score, 2)

        self.results.controls = [
            ft.Text("ئەنجامەکان", text_align=ft.TextAlign.END, size=25),
            ft.Text(f"ناو: {number_info['name']}"),
            ft.Text(f"ژمارە: {number}"),
            ft.Text(f"دڵنیای: %{score}"),
        ]

        await self.update_async()


async def main(page: ft.Page):
    page.rtl = True
    page.title = "رەقەم دۆزەرەوە"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    app = KurdishCaller()

    page.fonts = {
        "NRT-Bold": "fonts/NRT-Bd.ttf",
        "NRTReg": "fonts/NRT-Reg.ttf"
    }
    page.theme = ft.Theme(font_family="NRT-Bold")
    page.theme_mode = ft.ThemeMode.LIGHT
    await page.update_async()

    await page.add_async(app)


ft.app(target=main, assets_dir="assets")

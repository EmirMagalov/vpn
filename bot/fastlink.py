
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse

app = FastAPI()


@app.get("/config")
async def redirect_to_v2ray(v2ray_url: str):
    # Ссылка v2raytun

    # HTML страница с редиректом
    html_content = f"""
    <html>
        <body>
            <h2>Перенаправляем вас на приложение...</h2>
            <p>Если редирект не произошел автоматически, <a href="{v2ray_url}">нажмите здесь</a>, чтобы открыть ссылку в соответствующем приложении.</p>
            <script>
                window.location.href = "{v2ray_url}";
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
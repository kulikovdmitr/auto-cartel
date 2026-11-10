import json
import re
from datetime import date, datetime
from pathlib import Path

from fastapi import BackgroundTasks, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from . import catalog, notify

BASE = Path(__file__).resolve().parent.parent
BOOKINGS = BASE / "data" / "bookings.jsonl"
PHONE_RE = re.compile(r"^\+?[\d\s\-()]{10,18}$")

app = FastAPI(title="Autoservice prototype")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")
templates = Jinja2Templates(directory=BASE / "templates")


def render(request: Request, name: str, status: int = 200, **ctx) -> HTMLResponse:
    ctx.update(site=catalog.site(), services=catalog.services())
    return templates.TemplateResponse(request, name, ctx, status_code=status)


@app.get("/", response_class=HTMLResponse)
def index(request: Request, service: str | None = None):
    selected = [service] if service and catalog.by_slug(service) else []
    return render(request, "index.html", selected=selected, form={}, errors=[],
    today=date.today().isoformat())


@app.get("/uslugi/{slug}", response_class=HTMLResponse)
def service_page(request: Request, slug: str):
    item = catalog.by_slug(slug)
    if not item:
        raise HTTPException(404)
    return render(request, "service.html", item=item)


@app.post("/zapis", response_class=HTMLResponse)
def book(
    request: Request,
    background: BackgroundTasks,
    name: str = Form(""),
    phone: str = Form(""),
    car: str = Form(""),
    visit_date: str = Form(""),
    services: list[str] = Form(default=[]),
    consent: str = Form(""),
):
    chosen = [s for s in (catalog.by_slug(x) for x in services) if s]
    errors = []
    if not chosen:
        errors.append("Выберите хотя бы одну услугу.")
    if len(name.strip()) < 2:
        errors.append("Укажите имя.")
    if not PHONE_RE.match(phone.strip()):
        errors.append("Проверьте телефон: нужно 10–15 цифр.")
    if not car.strip():
        errors.append("Укажите марку и модель автомобиля.")
    if not consent:
        errors.append("Нужно согласие на обработку персональных данных.")

    if errors:
        form = dict(name=name, phone=phone, car=car, visit_date=visit_date)
        return render(request, "index.html", status=422, selected=services,
                      form=form, errors=errors, today=date.today().isoformat())

    record = {
        "created": datetime.now().isoformat(timespec="seconds"),
        "name": name.strip(), "phone": phone.strip(), "car": car.strip(),
        "visit_date": visit_date, "services": [s["slug"] for s in chosen],
        "total_from": sum(s["price_from"] for s in chosen),
        "consent": True,
    }
    BOOKINGS.parent.mkdir(exist_ok=True)
    with BOOKINGS.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
        background.add_task(
        notify.send_telegram,
        notify.booking_text(record, [s["title"] for s in chosen], catalog.site()["currency"]),
    )
    return RedirectResponse("/spasibo", status_code=303)


@app.get("/spasibo", response_class=HTMLResponse)
def thanks(request: Request):
    return render(request, "thanks.html")


@app.get("/privacy", response_class=HTMLResponse)
def privacy(request: Request):
    return render(request, "privacy.html")

# DDAEmpresariales6 — Motor de plantillas con Django

Laboratorio 06 de Desarrollo de Aplicaciones Empresariales (4-C24-A).
Portal de noticias con la app `news` (modelos `Author`, `Category` y `Article`), herencia de plantillas, un fragmento reutilizable y contenido gestionado desde el administrador.

## Cómo ejecutarlo

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py setup_demo     # 3 categorías, 2 autores, 6 noticias con imagen y el superusuario
python manage.py runserver
```

- Portal: http://127.0.0.1:8000/
- Administrador: http://127.0.0.1:8000/admin/ (usuario `admin`; contraseña de demostración `Admin12345!`, modificable con `DEMO_ADMIN_PASSWORD` antes de `setup_demo`).
- `SECRET_KEY` y `DEBUG` se leen de `DJANGO_SECRET_KEY` y `DJANGO_DEBUG`.

## Pruebas

```powershell
python manage.py test
```

## Estructura de plantillas

```
templates/
├── base.html                  # estructura común: cabecera, bloques title / content / sidebar, pie
└── news/
    ├── _article_card.html     # fragmento: tarjeta de una noticia
    ├── home.html              # portada (extends base, include de la tarjeta)
    ├── article_detail.html    # detalle (extends base, sobrescribe sidebar con block.super)
    └── category_detail.html   # listado por categoría (reutiliza la misma tarjeta)
static/css/styles.css          # hoja de estilos cargada con {% load static %}
```

Rutas (`news/urls.py`): `news:home`, `news:article_detail`, `news:category_detail`. Todos los enlaces usan `{% url %}`; no hay direcciones escritas a mano.

## Observaciones

- **Herencia y fragmento:** el marcado común vive solo en `base.html`. La tarjeta se escribe una vez en `_article_card.html` y se incluye con `{% include %}` desde la portada y desde el listado por categoría; si cambia, cambia en ambas páginas.
- **Variables, control y filtros:** la portada recorre las noticias con `{% for %}`, muestra un mensaje con `{% empty %}` cuando no hay resultados, recorta el resumen con `truncatewords:20` y da formato a la fecha con `date`. La lógica de consulta (`select_related`, `prefetch_related`, filtro por categoría) está en las vistas, no en las plantillas.
- **Barra lateral en todas las páginas:** las categorías llegan por un procesador de contexto (`news.context_processors.categories`), así ninguna vista tiene que pasarlas. El detalle de la noticia sobrescribe el bloque `sidebar` y conserva el original con `{{ block.super }}`.
- **Administrador:** las tres entidades tienen `list_display`, `list_filter` y `search_fields`; las noticias añaden `date_hierarchy`, `filter_horizontal` y `slug` autocompletado. Lo que se crea o edita en el panel aparece en el portal sin tocar código.
- **Estáticos y medios:** la hoja de estilos se enlaza con `{% static %}` y las imágenes con `article.featured_image.url`; `config/urls.py` sirve `MEDIA_ROOT` solo con `DEBUG` activo. La carpeta `media/` no se versiona: `setup_demo` regenera las imágenes de ejemplo.

## Prueba del escapado automático (paso 12)

Se guarda en el cuerpo de una noticia, desde el administrador, este texto:

```
<script>alert("x")</script> y <b>negrita</b>
```

**Qué muestra la página:** el texto tal cual, con las etiquetas visibles como caracteres; no se ejecuta ningún script y la palabra «negrita» no sale en negrita. En el código fuente de la página las etiquetas aparecen como `&lt;script&gt;…` y `&lt;b&gt;…&lt;/b&gt;`.

**Por qué:** Django escapa automáticamente toda variable que se imprime con `{{ }}`, convirtiendo `<`, `>`, `&`, `'` y `"` en entidades HTML. Así, el contenido escrito por un usuario no puede inyectar HTML ni JavaScript (XSS). El cuerpo se muestra con `linebreaks`, que respeta el escapado, y nunca con `|safe`. Marcar un texto como `|safe` o `{% autoescape off %}` desactivaría esa protección y solo sería aceptable con contenido de confianza. La prueba `test_html_in_body_is_escaped` lo comprueba automáticamente.

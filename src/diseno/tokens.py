"""Tokens del sistema de diseño de FRACTALL, portados 1:1 desde
fractall-frontend (docs/frontend-disenno.md, tailwind.config.ts,
app/globals.css). No modificar valores acá sin actualizar esa fuente
también — evita que los dos clientes diverjan visualmente."""

# Base neutra — papel cálido
PAPEL = "#F5F1E8"
LINO = "#FBF9F4"
ARENA = "#E2D9C7"
TINTA = "#2B2620"
GRAFITO = "#6B6255"

# Acento de marca
COSECHA = "#B9862F"
MUSGO = "#3F6656"

# Estados fiscales — paleta independiente de la de marca. Regla de diseño
# no negociable (frontend-disenno.md sección 2.3): nunca reutilizar estos
# valores para elementos de marca/CTA, ni viceversa.
ESTADO_ACEPTADO = "#3A7D5C"
ESTADO_RECHAZADO = "#B54A3F"
ESTADO_PENDIENTE = "#C99A3E"
ESTADO_ERROR_COMUNICACION = "#6B7280"

# Escala tipográfica — relación 1.25x, base 16px
FUENTE_XS = 10.24
FUENTE_SM = 12.8
FUENTE_BASE = 16.0
FUENTE_LG = 20.0
FUENTE_XL = 25.0
FUENTE_2XL = 31.25
FUENTE_3XL = 39.06

# Radios — base 8px (--radius: 0.5rem en globals.css)
RADIO_LG = 8.0
RADIO_MD = 6.0
RADIO_SM = 4.0
RADIO_SELLO = 999.0  # badge de estado — completamente redondeado

# Anchos de layout — app/(auth)/layout.tsx usa max-w-md (28rem) para
# centrar los formularios de auth.
ANCHO_FORMULARIO_AUTH = 448.0

# El sidebar fijo del frontend (w-56 = 224px) no es responsive — es un
# diseño solo-desktop. fractall-flet sí necesita empaquetarse para móvil,
# así que por debajo de este punto de quiebre el sidebar se reemplaza por
# un NavigationDrawer que se abre con el botón hamburguesa del topbar.
ANCHO_PUNTO_QUIEBRE_MOVIL = 768.0

# Nombres de familia registrados en page.fonts (ver diseno/tema.py).
# Los pesos disponibles (Regular/Medium/SemiBold) son los 3 que realmente
# usa fractall-frontend — confirmado por uso real de font-medium/
# font-semibold en el código, no por el máximo teórico del doc de diseño.
FUENTE_DISPLAY = "Bricolage Grotesque"
FUENTE_DISPLAY_MEDIUM = "Bricolage Grotesque Medium"
FUENTE_DISPLAY_SEMIBOLD = "Bricolage Grotesque SemiBold"
FUENTE_CUERPO = "Karla"
FUENTE_CUERPO_MEDIUM = "Karla Medium"
FUENTE_CUERPO_SEMIBOLD = "Karla SemiBold"
FUENTE_MONO = "IBM Plex Mono"
FUENTE_MONO_MEDIUM = "IBM Plex Mono Medium"

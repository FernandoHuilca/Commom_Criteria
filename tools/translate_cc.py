import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path('.')
EN = json.loads((ROOT / 'data/cc_en.json').read_text(encoding='utf-8'))
OLD = json.loads((ROOT / 'data/cc.json').read_text(encoding='utf-8'))
CACHE_PATH = ROOT / 'data/translate_cache.json'
OUT = ROOT / 'data/cc_es.json'

# Reuse curated Spanish names from the sample.
old_names = {}
for cls in OLD['classes']:
    old_names[cls['id']] = cls['name']
    for fam in cls['families']:
        old_names[fam['id']] = fam['name']
        for comp in fam['components']:
            old_names[comp['id']] = comp['name']

old_components = {}
for cls in OLD['classes']:
    for fam in cls['families']:
        for comp in fam['components']:
            old_components[comp['id']] = comp

name_overrides = {
    'FCO': 'Comunicación',
    'FTA': 'Acceso a la TOE',
    'FTP': 'Ruta y canales de confianza',
    'FDP_UCT': 'Protección de la confidencialidad de datos de usuario en transferencias inter-TSF',
    'FDP_UIT': 'Protección de la integridad de datos de usuario en transferencias inter-TSF',
    'FMT_MOF': 'Gestión de funciones de la TSF',
    'FMT_MSA': 'Gestión de atributos de seguridad',
    'FMT_MTD': 'Gestión de datos de la TSF',
    'FPT_EMS': 'Emanación de la TOE',
    'FPT_ITA': 'Disponibilidad de datos de la TSF exportados',
    'FPT_ITC': 'Confidencialidad de los datos de la TSF exportados',
    'FPT_ITI': 'Integridad de los datos de la TSF exportados',
    'FPT_ITT': 'Transferencia interna de datos de la TOE y la TSF',
    'FPT_PHP': 'Protección física de la TSF',
    'FPT_TDC': 'Coherencia de datos entre TSF',
    'FPT_TEE': 'Pruebas de entidades externas',
    'FPT_TRC': 'Coherencia de replicación interna de datos de la TSF',
    'FPT_TST': 'Autoprueba de la TSF',
    'FTA_TAB': 'Avisos de acceso a la TOE',
    'FTA_TSE': 'Establecimiento de sesión en la TOE',
    'FTP_ITC': 'Canal de confianza inter-TSF',
    'FTP_PRO': 'Protocolo de canal de confianza',
    'FTP_TRP': 'Ruta de confianza',
    'FCO_NRO.1': 'Prueba selectiva del origen',
    'FCO_NRR': 'No repudio de recepción',
    'FPT_SSP': 'Protocolo de sincronización de estado',
    'FPR_UNL': 'No vinculabilidad de las operaciones',
    'FCO_NRO.2': 'Prueba del origen obligatoria',
    'FCO_NRR.1': 'Prueba selectiva de recepción',
    'FCO_NRR.2': 'Prueba de recepción obligatoria',
    'FCS_CKM.3': 'Acceso a claves criptográficas',
    'FCS_CKM.5': 'Derivación de claves criptográficas',
    'FCS_CKM.6': 'Momento y evento de destrucción de claves criptográficas',
    'FCS_RBG.2': 'Generación de bits aleatorios (siembra externa)',
    'FCS_RBG.3': 'Generación de bits aleatorios (siembra interna: fuente única)',
    'FCS_RBG.4': 'Generación de bits aleatorios (siembra interna: múltiples fuentes)',
    'FCS_RBG.5': 'Generación de bits aleatorios (combinación de fuentes de ruido)',
    'FCS_RBG.6': 'Servicio de generación de bits aleatorios',
    'FCS_RNG': 'Generación de números aleatorios',
    'FIA_UAU.1': 'Momento de la autenticación',
    'FIA_UAU.6': 'Reautenticación',
    'FIA_UID.1': 'Momento de la identificación',
    'FMT_MOF.1': 'Gestión del comportamiento de las funciones de seguridad',
    'FMT_MSA.1': 'Gestión de atributos de seguridad',
    'FMT_MSA.3': 'Inicialización estática de atributos',
    'FMT_MTD.1': 'Gestión de datos de la TSF',
    'FMT_MTD.2': 'Gestión de límites de datos de la TSF',
    'FMT_MTD.3': 'Datos de la TSF seguros',
    'FMT_SAE.1': 'Caducidad de atributos de seguridad',
    'FMT_SMR.3': 'Asunción de roles',
    'FPR_PSE.2': 'Seudónimo reversible',
    'FPR_PSE.3': 'Seudónimo con alias',
    'FPT_EMS.1': 'Emanación de la TSF y datos de usuario',
    'FPT_FLS.1': 'Fallo con preservación del estado seguro',
    'FPT_ITA.1': 'Disponibilidad de datos de la TSF exportados dentro de una métrica definida',
    'FPT_ITC.1': 'Confidencialidad de datos de la TSF exportados durante la transmisión',
    'FPT_ITI.1': 'Detección de modificaciones en datos de la TSF exportados',
    'FPT_ITI.2': 'Detección y corrección de modificaciones en datos de la TSF exportados',
    'FPT_ITT.1': 'Protección básica de transferencia interna de datos de la TSF',
    'FPT_ITT.2': 'Separación de transferencia de datos de la TSF',
    'FPT_ITT.3': 'Supervisión de integridad de datos de la TSF',
    'FPT_PHP.2': 'Notificación de ataque físico',
    'FPT_RCV.1': 'Recuperación manual',
    'FPT_RPL.1': 'Detección de repeticiones',
    'FPT_SSP.1': 'Acuse de recibo de confianza simple',
    'FPT_SSP.2': 'Acuse de recibo mutuo de confianza',
    'FPT_STM.2': 'Fuente de tiempo',
    'FPT_TDC.1': 'Coherencia básica de datos de la TSF entre TSF',
    'FPT_TEE.1': 'Pruebas de entidades externas',
    'FPT_TRC.1': 'Coherencia interna de la TSF',
    'FPT_TST.1': 'Autoprueba de la TSF',
    'FTA_MCS.1': 'Limitación básica de sesiones simultáneas múltiples',
    'FTA_MCS.2': 'Limitación por atributo de usuario de sesiones simultáneas múltiples',
    'FTA_SSL.1': 'Bloqueo de sesión iniciado por la TSF',
    'FTA_SSL.3': 'Terminación iniciada por la TSF',
    'FTA_TAB.1': 'Avisos de acceso a la TOE predeterminados',
    'FTA_TSE.1': 'Establecimiento de sesión en la TOE',
    'FTP_ITC.1': 'Canal de confianza inter-TSF',
    'FTP_PRO.2': 'Establecimiento de canal de confianza',
    'FTP_PRO.3': 'Protección de datos del canal de confianza',
    'FTP_TRP.1': 'Ruta de confianza',
}

cache = json.loads(CACHE_PATH.read_text(encoding='utf-8')) if CACHE_PATH.exists() else {}

TRANSLATABLE_KEYS = []


def add(key, text):
    text = normalize_source(text)
    if text:
        TRANSLATABLE_KEYS.append((key, text))


def normalize_source(text):
    text = re.sub(r'\s+', ' ', str(text or '')).strip()
    text = re.sub(r'(?<=\w)- (?=\w)', '-', text)
    return text


classes = EN['classes']
for cls in classes:
    add(('class', cls['id'], 'name'), cls['name'])
    add(('class', cls['id'], 'desc'), cls['description'])
    for fam in cls['families']:
        add(('family', fam['id'], 'name'), fam['name'])
        add(('family', fam['id'], 'desc'), fam['description'])
        for comp in fam['components']:
            add(('comp', comp['id'], 'name'), comp['name'])
            add(('comp', comp['id'], 'summary'), comp['description'])
            for i, item in enumerate(comp['management']):
                add(('comp', comp['id'], 'mgmt', i), item)
            for i, item in enumerate(comp['audit']):
                item_text = normalize_source(item)
                m = re.match(r'(?i)^(?:minimal|basic|detailed|ddetailed)\s*:\s*(.*)$', item_text)
                add(('comp', comp['id'], 'audit', i), m.group(1) if m else item_text)
            for el in comp['elements']:
                for bi, block in enumerate(el['blocks']):
                    if block['type'] == 'p':
                        add(('element', el['id'], 'p', bi), block['text'])
                    else:
                        for ii, item in enumerate(block['items']):
                            add(('element', el['id'], 'item', bi, ii), item)

# Curated summaries for the nine complete cards.
for cid, comp in old_components.items():
    if comp.get('available') and comp.get('summary'):
        for key, text in TRANSLATABLE_KEYS:
            if key[:3] == ('comp', cid, 'summary'):
                cache[text] = comp['summary']

# Curated names, except where the old sample used a clearly provisional wording.
for key, text in TRANSLATABLE_KEYS:
    if key[2] == 'name' and key[1] in old_names:
        cache.setdefault(text, old_names[key[1]])

# Normalize source before translation.
def preprocess(text):
    text = re.sub(r'\bShall\b', 'Must', text)
    text = re.sub(r'\bshall\b', 'must', text)
    text = re.sub(r'\bShould\b', 'should', text)
    return text


def protect(text):
    return (text.replace('TSF', 'TSF').replace('TOE', 'TOE')
            .replace('PP-Module', 'PP-Module'))


def postprocess(text):
    text = text.replace('\u00ad', '').replace('\ufffd', '')
    text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    # Deontic language
    text = re.sub(r'\bdeben\b', 'deberán', text)
    text = re.sub(r'\bdebe\b', 'deberá', text)
    text = re.sub(r'\bdeberia\b', 'debería', text)
    text = re.sub(r'\bdeberian\b', 'deberían', text)
    # Gender and agreement for the standard entities
    text = re.sub(r'\bEl TSF\b', 'La TSF', text)
    text = re.sub(r'\bel TSF\b', 'la TSF', text)
    text = re.sub(r'\bdel TSF\b', 'de la TSF', text)
    text = re.sub(r'\bal TSF\b', 'a la TSF', text)
    text = re.sub(r'\bEl TOE\b', 'La TOE', text)
    text = re.sub(r'\bel TOE\b', 'la TOE', text)
    text = re.sub(r'\bdel TOE\b', 'de la TOE', text)
    text = re.sub(r'\bal TOE\b', 'a la TOE', text)
    text = re.sub(r'\bun TOE\b', 'una TOE', text)
    text = re.sub(r'\bUn TOE\b', 'Una TOE', text)
    text = re.sub(r'\blos TOE\b', 'las TOE', text)
    text = re.sub(r'\beste TOE\b', 'esta TOE', text)
    text = re.sub(r'\bTOE distribuidos\b', 'TOE distribuidas', text)
    text = re.sub(r'\bTOE monolíticos\b', 'TOE monolíticas', text)
    text = re.sub(r'\bTOE estructurado\b', 'TOE estructurada', text)
    text = re.sub(r'\bTOE esté protegido\b', 'TOE esté protegida', text)
    text = re.sub(r'\bun TSF\b', 'una TSF', text)
    text = re.sub(r'\bUn TSF\b', 'Una TSF', text)
    text = re.sub(r'\blos TSF\b', 'las TSF', text)
    text = re.sub(r'\beste TSF\b', 'esta TSF', text)
    text = re.sub(r'\bTSF esté protegido\b', 'TSF esté protegida', text)
    # Common terminology
    text = text.replace('PP-Módulo', 'módulo de PP').replace('PP-Módulo', 'módulo de PP')
    text = re.sub(r'\b[Mm]ódulo PP\b', 'módulo de PP', text)
    text = re.sub(r'\bPP-Modules\b', 'módulos de PP', text)
    text = re.sub(r'\bPP-Module\b', 'módulo de PP', text)
    text = re.sub(r'\bJerárquico (?:para|a)\b', 'Jerárquico respecto a', text)
    text = re.sub(r'\bNo hay otros componentes\.?', 'Ningún otro componente.', text)
    text = re.sub(r'\bNo hay dependencias\.?', 'Sin dependencias.', text)
    text = re.sub(r'\bdeberá ser capaz de\b', 'deberá poder', text)
    text = re.sub(r'\bdeberán ser capaces de\b', 'deberán poder', text)
    text = text.replace('hacer cumplir', 'aplicar')
    text = text.replace('dedo del pie', 'TOE')
    text = text.replace('dedos de los pies', 'TOE')
    text = re.sub(r'\bBanners\b', 'Avisos', text)
    text = re.sub(r'\bbanners\b', 'avisos', text)
    text = text.replace('camino confiable', 'ruta de confianza')
    text = text.replace('Camino confiable', 'Ruta de confianza')
    text = re.sub(r'\bpseudónimo\b', 'seudónimo', text)
    text = re.sub(r'\bPseudónimo\b', 'Seudónimo', text)
    text = re.sub(r'\bmonitoreo\b', 'supervisión', text)
    text = re.sub(r'\bMonitoreo\b', 'Supervisión', text)
    text = re.sub(r'\bmonitorear\b', 'supervisar', text)
    text = re.sub(r'\bMonitorear\b', 'Supervisar', text)
    text = text.replace('con base en', 'basándose en')
    text = text.replace('Con base en', 'Basándose en')
    text = text.replace('pista de auditoría', 'registro de auditoría')
    text = text.replace('constancia de recibo', 'evidencia de recepción')
    text = text.replace('comprobante de recibo', 'evidencia de recepción')
    text = text.replace('canal confiable', 'canal de confianza')
    text = text.replace('Canales confiables', 'Canales de confianza')
    text = text.replace('canales confiables', 'canales de confianza')
    text = text.replace('ruta confiable', 'ruta de confianza')
    text = text.replace('Ruta confiable', 'Ruta de confianza')
    text = text.replace('producto de TI confiable', 'producto de TI de confianza')
    text = text.replace('productos de TI confiables', 'productos de TI de confianza')
    text = text.replace('TOE Emanación', 'Emanación de la TOE')
    text = text.replace('a este tema', 'a este sujeto')
    text = text.replace('este tema', 'este sujeto')
    text = text.replace('objetivo del establecimiento', 'destino del establecimiento')
    text = text.replace('La consecución del umbral', 'Alcanzar el umbral')
    text = text.replace('la consecución del umbral', 'alcanzar el umbral')
    text = re.sub(r'\blímite límite\b', 'límite', text)
    text = re.sub(r'\bSFRs\b', 'SFR', text)
    text = text.replace('él mismo', 'ella misma')
    text = text.replace('sí mismo', 'sí misma')
    text = text.replace('la función de inicialización TOE', 'la función de inicialización de la TOE')
    text = text.replace('plataforma TOE', 'plataforma de la TOE')
    text = re.sub(r'\bBanners\b', 'Avisos', text)
    text = re.sub(r'\bbanners\b', 'avisos', text)
    text = re.sub(r'\bBanner\b', 'Aviso', text)
    text = re.sub(r'\bbanner\b', 'aviso', text)
    text = text.replace('[asignación: control de acceso SFP]', '[asignación: SFP de control de acceso]')
    text = text.replace('[asignación: control de flujo de información SFP]', '[asignación: SFP de control de flujo de información]')
    text = re.sub(r'control de acceso SFP\(s\)', 'SFP(s) de control de acceso', text)
    text = re.sub(r'control de flujo de información SFP\(s\)', 'SFP(s) de control de flujo de información', text)
    text = re.sub(r'SFP de control de acceso identificado', 'SFP de control de acceso identificada', text)
    text = re.sub(r'SFP de control de flujo de información identificado', 'SFP de control de flujo de información identificada', text)
    # SFP is feminine (política de seguridad funcional)
    text = re.sub(r'\bel SFP\b', 'la SFP', text)
    text = re.sub(r'\bdel SFP\b', 'de la SFP', text)
    text = re.sub(r'\bal SFP\b', 'a la SFP', text)
    text = re.sub(r'\blos SFP\b', 'las SFP', text)
    text = re.sub(r'\bun SFP\b', 'una SFP', text)
    # TSF compounds
    text = re.sub(r'\bdatos TSF\b', 'datos de la TSF', text)
    text = re.sub(r'\bDatos TSF\b', 'Datos de la TSF', text)
    text = re.sub(r'\bfunciones TSF\b', 'funciones de la TSF', text)
    text = re.sub(r'\bFunciones TSF\b', 'Funciones de la TSF', text)
    text = re.sub(r'\bentre TSF\b', 'entre TSF', text)
    text = re.sub(r'\bTOE TSF\b', 'TOE y TSF', text)
    text = text.replace('[tarea:', '[asignación:')
    text = text.replace('[Tarea:', '[Asignación:')
    text = text.replace('[seleccion:', '[selección:')
    text = text.replace('[asignacion:', '[asignación:')
    text = text.replace('[iteracion:', '[iteración:')
    text = text.replace('[refinamiento:', '[refinamiento:')
    text = re.sub(r'\bTOE\b', 'TOE', text)
    # Cleanup punctuation
    text = re.sub(r'\s+([,.;:!?])', r'\1', text)
    text = re.sub(r'\(\s+', '(', text)
    text = re.sub(r'\s+\)', ')', text)
    return text


import subprocess

def fetch_url(url):
    proc = subprocess.run(
        ['curl', '-sS', '-A', 'Mozilla/5.0', '--max-time', '40', url],
        capture_output=True, text=True, encoding='utf-8'
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or 'curl failed')
    return proc.stdout


def translate_batch(texts):
    joined = '\n\n<<<SEG>>>\n\n'.join(preprocess(t) for t in texts)
    url = 'https://translate.googleapis.com/translate_a/single'
    params = {
        'client': 'gtx',
        'sl': 'en',
        'tl': 'es',
        'dt': 't',
        'q': joined,
    }
    full_url = url + '?' + urllib.parse.urlencode(params)
    for attempt in range(5):
        try:
            out = fetch_url(full_url)
            payload = json.loads(out)
            translated = ''.join(piece[0] for piece in payload[0] if piece and piece[0])
            parts = re.split(r'\s*<<<\s*SEG\s*>>>\s*', translated)
            if len(parts) == len(texts):
                return [postprocess(p) for p in parts]
        except Exception as exc:
            print('retry', attempt, exc)
        time.sleep(1.5 * (attempt + 1))
    # Fall back to one request per segment
    results = []
    for text in texts:
        full_url = 'https://translate.googleapis.com/translate_a/single?' + urllib.parse.urlencode({
            'client': 'gtx', 'sl': 'en', 'tl': 'es', 'dt': 't', 'q': preprocess(text)
        })
        payload = json.loads(fetch_url(full_url))
        results.append(postprocess(''.join(piece[0] for piece in payload[0] if piece and piece[0])))
        time.sleep(0.2)
    return results


pending = []
for key, text in TRANSLATABLE_KEYS:
    if text not in cache:
        pending.append((key, text))

# Unique pending texts
unique = []
seen = set()
for _, text in pending:
    if text not in seen:
        seen.add(text)
        unique.append(text)

print('segments', len(TRANSLATABLE_KEYS), 'unique pending', len(unique), file=__import__('sys').stderr)

batch = []
length = 0
batches = []
for text in unique:
    if batch and length + len(text) + 15 > 4200:
        batches.append(batch)
        batch = []
        length = 0
    batch.append(text)
    length += len(text) + 15
if batch:
    batches.append(batch)

for bi, batch in enumerate(batches):
    print('batch', bi + 1, '/', len(batches), 'segments', len(batch), file=__import__('sys').stderr)
    translated = translate_batch(batch)
    if len(translated) != len(batch):
        raise SystemExit('translation length mismatch')
    for src, dst in zip(batch, translated):
        cache[src] = dst
    if bi % 5 == 0:
        CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')
    time.sleep(0.25)

CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding='utf-8')


def tr(key, text):
    text = normalize_source(text)
    return postprocess(cache.get(text, text)) if text else ''


level_map = {'minimal': 'mínimo', 'basic': 'básico', 'detailed': 'detallado', 'ddetailed': 'detallado'}


def clean_name(value, item_id=''):
    value = name_overrides.get(item_id, value)
    value = postprocess(normalize_source(value))
    value = re.sub(r'[.\s]+$', '', value)
    if value:
        value = value[0].upper() + value[1:]
    return value


final_names = {}
for cls in classes:
    final_names[cls['id']] = clean_name(old_names.get(cls['id']) or cache.get(normalize_source(cls['name']), cls['name']), cls['id'])
    for fam in cls['families']:
        final_names[fam['id']] = clean_name(old_names.get(fam['id']) or cache.get(normalize_source(fam['name']), fam['name']), fam['id'])
        for comp in fam['components']:
            final_names[comp['id']] = clean_name(old_names.get(comp['id']) or cache.get(normalize_source(comp['name']), comp['name']), comp['id'])


def clean_summary(cid, text):
    text = postprocess(normalize_source(text))
    text = re.sub(r'^' + re.escape(cid) + r'\s*', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if text:
        text = text[0].upper() + text[1:]
    return text


def clean_es(text):
    text = normalize_source(text)
    if text:
        text = text[0].upper() + text[1:]
    return text


def parse_audit(item):
    item = normalize_source(item)
    m = re.match(r'(?i)^(minimal|basic|detailed|ddetailed)\s*:\s*(.*)$', item)
    if m:
        return {'level': level_map[m.group(1).lower()], 'text': clean_es(postprocess(cache.get(m.group(2), m.group(2))))}
    return {'level': 'nota', 'text': clean_es(postprocess(cache.get(item, item)))}


colors = {
    'FAU': '#b97a1f', 'FCO': '#7a5c9e', 'FCS': '#2f7f86', 'FDP': '#356a9a',
    'FIA': '#4a7b45', 'FMT': '#8a5a44', 'FPR': '#a34d6a', 'FPT': '#4f6478',
    'FRU': '#6b7d3a', 'FTA': '#b65d3b', 'FTP': '#3f6f8f'
}

out_classes = []
for cls in classes:
    out_cls = {
        'id': cls['id'],
        'number': cls['number'],
        'name': final_names[cls['id']],
        'nameEn': cls['name'],
        'color': colors.get(cls['id'], '#5b6b7a'),
        'description': clean_es(tr(('class', cls['id'], 'desc'), cls['description'])),
        'keywords': [],
        'families': []
    }
    for fam in cls['families']:
        out_fam = {
            'id': fam['id'],
            'number': fam['number'],
            'name': final_names[fam['id']],
            'nameEn': fam['name'],
            'description': clean_es(tr(('family', fam['id'], 'desc'), fam['description'])),
            'keywords': [],
            'components': []
        }
        for comp in fam['components']:
            summary = cache.get(normalize_source(comp['description']), '')
            if not summary:
                summary = tr(('comp', comp['id'], 'summary'), comp['description'])
            out_comp = {
                'id': comp['id'],
                'name': final_names[comp['id']],
                'nameEn': comp['name'],
                'available': True,
                'summary': clean_summary(comp['id'], summary),
                'hierarchicalTo': [{'id': x['id'], 'name': final_names[x['id']]} for x in comp['hierarchicalTo']],
                'dependencies': [{'id': x['id'], 'name': final_names[x['id']]} for x in comp['dependencies']],
                'management': [clean_es(tr(('comp', comp['id'], 'mgmt', i), x)) for i, x in enumerate(comp['management'])],
                'audit': [parse_audit(x) for x in comp['audit']],
                'keywords': [],
                'elements': []
            }
            for el in comp['elements']:
                blocks = []
                for bi, block in enumerate(el['blocks']):
                    if block['type'] == 'p':
                        blocks.append({'type': 'p', 'text': tr(('element', el['id'], 'p', bi), block['text'])})
                    else:
                        blocks.append({
                            'type': 'list',
                            'ordered': block['ordered'],
                            'items': [tr(('element', el['id'], 'item', bi, ii), item) for ii, item in enumerate(block['items'])]
                        })
                out_comp['elements'].append({'id': el['id'], 'blocks': blocks})
            out_fam['components'].append(out_comp)
        out_cls['families'].append(out_fam)
    out_classes.append(out_cls)

meta = {
    'title': 'Atlas CC',
    'subtitle': 'Explorador de Criterios Comunes',
    'document': 'CC:2022 · Parte 2 · Revisión 1',
    'documentLong': 'Common Criteria for Information Technology Security Evaluation, Part 2: Security functional components',
    'version': 'Noviembre de 2022',
    'sourceUrl': 'https://www.commoncriteriaportal.org/cc/',
    'language': 'es',
    'translationNote': 'Traducción de estudio no oficial. En caso de discrepancia, prevalece el texto oficial en inglés.',
    'demo': False,
    'demoNote': '',
    'documentCounts': {'classes': 11, 'families': 74, 'components': 156, 'elements': 284}
}

OUT.write_text(json.dumps({'meta': meta, 'classes': out_classes}, ensure_ascii=False, indent=2), encoding='utf-8')
print('written', OUT, file=__import__('sys').stderr)

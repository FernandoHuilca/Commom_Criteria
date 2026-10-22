/* Common Criteria — vistas de la aplicación. */
(function (global) {
  'use strict';

  const CC = global.CC;
  const utils = CC.utils;
  const e = utils.escapeHtml;
  const icon = utils.icon;

  const TYPE_LABELS = {
    all: 'Todo',
    class: 'Clases',
    family: 'Familias',
    component: 'Componentes',
    element: 'Elementos'
  };

  const TYPE_ORDER = ['all', 'class', 'family', 'component', 'element'];

  const TYPE_SINGULAR = {
    class: 'Clase',
    family: 'Familia',
    component: 'Componente',
    element: 'Elemento'
  };

  function data() {
    return CC.data;
  }

  function padNumber(value) {
    return String(value).padStart(2, '0');
  }

  function classStyle(cls) {
    return '--class-color:' + e(cls.color || '#b4432c');
  }

  function classBadge(cls) {
    return '<span class="class-dot" style="' + classStyle(cls) + '" aria-hidden="true"></span>';
  }

  function classByComponent(component) {
    return data().maps.classById.get(component.classId);
  }

  function familyByComponent(component) {
    return data().maps.familyById.get(component.familyId);
  }

  function breadcrumbs(items) {
    return '<nav class="breadcrumbs" aria-label="Ruta de navegación"><ol>' + items.map(function (item, index) {
      const last = index === items.length - 1;
      if (last || !item.href) {
        return '<li><span aria-current="' + (last ? 'page' : 'false') + '">' + e(item.label) + '</span></li>';
      }
      return '<li><a href="' + e(item.href) + '">' + e(item.label) + '</a></li>';
    }).join('') + '</ol></nav>';
  }

  function sectionHead(eyebrow, title, lede, action) {
    return '<div class="section-head">' +
      '<div>' +
        '<p class="eyebrow">' + e(eyebrow) + '</p>' +
        '<h2>' + e(title) + '</h2>' +
        (lede ? '<p class="section-lede">' + e(lede) + '</p>' : '') +
      '</div>' +
      (action ? '<div class="section-action">' + action + '</div>' : '') +
    '</div>';
  }

  function renderHeroCard() {
    return '<aside class="hero-card-wrap" aria-hidden="true">' +
      '<div class="hero-card">' +
        '<span class="hero-card-tab">Expediente 08</span>' +
        '<div class="hero-card-head"><span>CC:2022 · PARTE 2</span><span>08 / 11</span></div>' +
        '<div class="hero-card-code">FAU</div>' +
        '<h2>Auditoría de seguridad</h2>' +
        '<p class="hero-card-lede">Del requisito general al elemento verificable.</p>' +
        '<div class="hero-card-rule"></div>' +
        '<dl class="hero-card-path">' +
          '<div><dt>Clase</dt><dd>FAU</dd></div>' +
          '<div><dt>Familia</dt><dd>FAU_ARP</dd></div>' +
          '<div><dt>Componente</dt><dd>FAU_ARP.1</dd></div>' +
          '<div><dt>Elemento</dt><dd>FAU_ARP.1.1</dd></div>' +
        '</dl>' +
        '<div class="hero-card-foot"><span>Clase</span><span>Familia</span><span>Componente</span><span>Elemento</span></div>' +
      '</div>' +
    '</aside>';
  }

  function renderClassCard(cls) {
    return '<a class="class-card" href="' + e(cls.href) + '" style="' + classStyle(cls) + '">' +
      '<div class="class-card-top">' +
        '<span class="class-number">' + padNumber(cls.number) + '</span>' +
        '<span class="class-code">' + e(cls.id) + '</span>' +
        '<span class="class-arrow">' + icon('arrow-up-right') + '</span>' +
      '</div>' +
      '<h3>' + e(cls.name) + '</h3>' +
      '<p>' + e(cls.description) + '</p>' +
      '<div class="class-card-meta">' +
        '<span>' + cls.familyCount + ' ' + utils.pluralize(cls.familyCount, 'familia', 'familias') + '</span>' +
        '<span>' + cls.componentCount + ' ' + utils.pluralize(cls.componentCount, 'componente', 'componentes') + '</span>' +
      '</div>' +
    '</a>';
  }

  function renderHome() {
    const d = data();
    const meta = d.meta;
    const documentCounts = meta.documentCounts || d.stats;

    const stats = [
      { value: documentCounts.classes, label: 'clases' },
      { value: documentCounts.families, label: 'familias' },
      { value: documentCounts.components, label: 'componentes' },
      { value: documentCounts.elements, label: 'elementos' }
    ];

    return '<section class="hero">' +
      '<div class="container hero-grid">' +
        '<div class="hero-copy">' +
          '<p class="eyebrow"><span class="eyebrow-rule"></span> CC:2022 · Parte 2 · Componentes funcionales</p>' +
          '<h1>El mapa para estudiar <em>Common Criteria.</em></h1>' +
          '<p class="hero-lede">Busca, comprende y recorre la estructura del estándar desde la clase hasta el elemento. Todo en español, sin perder el contexto normativo.</p>' +
          '<form class="hero-search" data-search-form role="search">' +
            '<label class="sr-only" for="hero-search">Buscar en Criterios Comunes</label>' +
            '<div class="search-field">' +
              icon('search') +
              '<input id="hero-search" name="q" type="search" placeholder="Ej. FAU_ARP.1, auditoría, control de acceso…" autocomplete="off" spellcheck="false">' +
              '<button class="button button-primary" type="submit">Buscar ' + icon('arrow-right') + '</button>' +
            '</div>' +
          '</form>' +
          '<div class="quick-searches" aria-label="Búsquedas sugeridas">' +
            '<span class="quick-label">Prueba con</span>' +
            '<a href="#/buscar?q=auditor%C3%ADa">auditoría</a>' +
            '<a href="#/buscar?q=control%20de%20acceso">control de acceso</a>' +
            '<a href="#/buscar?q=autenticaci%C3%B3n">autenticación</a>' +
            '<a href="#/componente/FAU_ARP.1">FAU_ARP.1</a>' +
          '</div>' +
          '<dl class="hero-stats">' +
            stats.map(function (stat) {
              return '<div><dt>' + stat.label + '</dt><dd>' + e(utils.formatNumber(stat.value)) + '</dd></div>';
            }).join('') +
          '</dl>' +
          '<p class="hero-stats-note">Cifras del catálogo completo de la Parte 2.</p>' +
        '</div>' +
        renderHeroCard() +
      '</div>' +
    '</section>' +
    '<section class="section section-first">' +
      '<div class="container">' +
        sectionHead('01 · Catálogo', 'Explora por clase', 'Cada clase agrupa familias y componentes que abordan un mismo objetivo de seguridad.', '<a class="text-link" href="#/catalogo">Ver catálogo completo ' + icon('arrow-right') + '</a>') +
        '<div class="class-grid">' + d.classes.map(renderClassCard).join('') + '</div>' +
      '</div>' +
    '</section>' +
    '<section class="section section-alt">' +
      '<div class="container">' +
        sectionHead('02 · Estructura', 'Una jerarquía, cuatro niveles', 'Criterios Comunes organiza los requisitos funcionales de lo general a lo concreto. Esta es la ruta que sigue cada ficha.') +
        '<div class="hierarchy-grid">' +
          '<article class="hierarchy-card"><span class="hierarchy-num">01</span><h3>Clase</h3><p>Agrupa familias que comparten un área de seguridad, como auditoría o autenticación.</p><code>FAU</code></article>' +
          '<article class="hierarchy-card"><span class="hierarchy-num">02</span><h3>Familia</h3><p>Reúne componentes relacionados con un mismo tipo de requisito.</p><code>FAU_ARP</code></article>' +
          '<article class="hierarchy-card"><span class="hierarchy-num">03</span><h3>Componente</h3><p>Es la unidad normativa que se selecciona e incluye en un perfil de protección o en una ST.</p><code>FAU_ARP.1</code></article>' +
          '<article class="hierarchy-card"><span class="hierarchy-num">04</span><h3>Elemento</h3><p>Es cada declaración normativa que compone el requisito y que debe satisfacerse.</p><code>FAU_ARP.1.1</code></article>' +
        '</div>' +
      '</div>' +
    '</section>' +
    '</section>';
  }

  function renderCatalogSidebar(activeClassId) {
    const d = data();

    return '<aside class="catalog-sidebar" aria-label="Navegación del catálogo">' +
      '<p class="sidebar-title">Clases</p>' +
      '<nav class="class-nav">' +
        d.classes.map(function (cls) {
          const active = cls.id === activeClassId;
          return '<a class="class-nav-item' + (active ? ' is-active' : '') + '" href="' + e(cls.href) + '" style="' + classStyle(cls) + '"' + (active ? ' aria-current="page"' : '') + '>' +
            '<span class="class-nav-code">' + e(cls.id) + '</span>' +
            '<span class="class-nav-copy"><strong>' + e(cls.name) + '</strong><small>' + cls.familyCount + ' familias · ' + cls.componentCount + ' componentes</small></span>' +
          '</a>';
        }).join('') +
      '</nav>' +
    '</aside>';
  }

  function renderFamilySection(family, cls, open) {
    const completeCount = family.components.filter(function (component) {
      return component.available;
    }).length;
    const components = family.components.map(function (component) {
      const elementCount = component.elements.length;
      return '<a class="component-row" href="' + e(component.href) + '">' +
        '<span class="component-row-id">' + e(component.id) + '</span>' +
        '<span class="component-row-main">' +
          '<strong>' + e(component.name) + '</strong>' +
          '<small>' + elementCount + ' ' + utils.pluralize(elementCount, 'elemento', 'elementos') + '</small>' +
        '</span>' +
        '<span class="row-status ' + (component.available ? 'is-ready' : 'is-pending') + '">' +
          (component.available ? icon('check-circle') + ' Ficha completa' : 'En preparación') +
        '</span>' +
        '<span class="component-row-arrow" aria-hidden="true">' + icon('arrow-right') + '</span>' +
      '</a>';
    }).join('');

    return '<details class="family-section"' + (open ? ' open' : '') + ' id="familia-' + e(family.id) + '" data-family-section="' + e(family.id) + '">' +
      '<summary class="family-summary">' +
        '<span class="family-summary-copy">' +
          '<span class="eyebrow family-kicker"><span class="class-dot" aria-hidden="true"></span><span>' + e(cls.id) + '</span><span class="family-kicker-sep">·</span><span>Familia</span><strong>' + e(family.id) + '</strong></span>' +
          '<h2>' + e(family.name) + '</h2>' +
        '</span>' +
        '<span class="family-toggle" aria-hidden="true">' + icon('chevron-down') + '</span>' +
      '</summary>' +
      '<span class="family-watermark" aria-hidden="true">' + e(family.id) + '</span>' +
      '<div class="family-section-body">' +
        (family.description ? '<p class="family-section-lede">' + e(family.description) + '</p>' : '') +
        '<div class="metadata-row">' +
          '<span>' + icon('layers') + family.componentCount + ' ' + utils.pluralize(family.componentCount, 'componente', 'componentes') + '</span>' +
          '<span>' + icon('check-circle') + completeCount + ' ' + utils.pluralize(completeCount, 'ficha completa', 'fichas completas') + '</span>' +
          '<a href="' + e(cls.href) + '">Clase ' + e(cls.id) + '</a>' +
        '</div>' +
        '<div class="family-components">' +
          '<div class="family-components-head"><h3>Componentes</h3><span class="family-components-count">' + family.componentCount + '</span></div>' +
          '<div class="family-component-list">' + components + '</div>' +
        '</div>' +
      '</div>' +
    '</details>';
  }

  function renderCatalog() {
    const d = data();
    return '<section class="page-head page-head-compact">' +
      '<div class="container">' +
        '<p class="eyebrow">Catálogo</p>' +
        '<h1>Clases de Common Criteria</h1>' +
        '<p class="page-lede">Busca un requisito o elige una clase para recorrer sus familias, componentes y elementos.</p>' +
        '<form class="catalog-search" data-search-form role="search">' +
          '<label class="sr-only" for="catalog-search-input">Buscar en Common Criteria</label>' +
          '<div class="search-field">' +
            icon('search') +
            '<input id="catalog-search-input" name="q" type="search" placeholder="Ej. FAU_ARP.1, auditoría, control de acceso…" autocomplete="off" spellcheck="false">' +
            '<button class="button button-primary" type="submit">Buscar ' + icon('arrow-right') + '</button>' +
          '</div>' +
        '</form>' +
      '</div>' +
    '</section>' +
    '<div class="container catalog-clean">' +
      '<div class="class-grid class-grid-wide">' + d.classes.map(renderClassCard).join('') + '</div>' +
    '</div>';
  }

  function renderClassPage(cls, targetFamilyId) {
    const completeCount = cls.families.reduce(function (total, family) {
      return total + family.components.filter(function (component) { return component.available; }).length;
    }, 0);

    return '<section class="class-hero" style="' + classStyle(cls) + '">' +
      '<div class="container">' +
        breadcrumbs([
          { label: 'Inicio', href: '#/' },
          { label: 'Catálogo', href: '#/catalogo' },
          { label: cls.id, href: cls.href }
        ]) +
        '<div class="class-hero-grid">' +
          '<div class="class-hero-copy">' +
            '<p class="eyebrow">Clase ' + padNumber(cls.number) + ' · ' + e(cls.id) + '</p>' +
            '<h1>' + e(cls.name) + '</h1>' +
            '<p class="page-lede">' + e(cls.description) + '</p>' +
            '<div class="metadata-row">' +
              '<span>' + icon('layers') + cls.familyCount + ' ' + utils.pluralize(cls.familyCount, 'familia', 'familias') + '</span>' +
              '<span>' + icon('file') + cls.componentCount + ' ' + utils.pluralize(cls.componentCount, 'componente', 'componentes') + '</span>' +
              '<span>' + icon('check-circle') + completeCount + ' fichas completas</span>' +
            '</div>' +
          '</div>' +
          '<div class="class-hero-code" aria-hidden="true">' + e(cls.id) + '</div>' +
        '</div>' +
      '</div>' +
    '</section>' +
    '<div class="container catalog-shell catalog-shell-page" style="' + classStyle(cls) + '">' +
      renderCatalogSidebar(cls.id) +
      '<div class="catalog-main">' +
        '<div class="family-sections">' +
          cls.families.map(function (family) {
            return renderFamilySection(family, cls, family.id === targetFamilyId);
          }).join('') +
        '</div>' +
      '</div>' +
    '</div>';
  }

  function resultTop(doc, query) {
    return '<div class="result-kicker">' +
      '<span class="kind-badge kind-' + e(doc.kind) + '">' + e(TYPE_SINGULAR[doc.kind] || doc.kind) + '</span>' +
      (doc.kind !== 'element' ? '<span class="result-id">' + utils.highlight(doc.id, query) + '</span>' : '') +
      '<span class="result-context">' + e(doc.context || '') + '</span>' +
    '</div>';
  }

  function renderSearchResult(item, query) {
    const doc = item.doc;
    const title = doc.kind === 'element' ? 'Elemento ' + doc.id : doc.title;
    return '<a class="result-card result-' + e(doc.kind) + '" href="' + e(doc.href) + '">' +
      '<div class="result-body">' +
        resultTop(doc, query) +
        '<h3 class="result-title">' + utils.highlight(title, query) + '</h3>' +
        '<p class="result-snippet">' + utils.highlight(item.snippet, query) + '</p>' +
      '</div>' +
      '<span class="result-arrow">' + icon('arrow-right') + '</span>' +
    '</a>';
  }

  function renderSearchStart() {
    const d = data();
    return '<div class="search-start">' +
      '<div class="search-start-mark">' + icon('compass') + '</div>' +
      '<h2>Busca por concepto, identificador o texto normativo</h2>' +
      '<p>El índice es local y está pensado para el español: ignora tildes y mayúsculas, reconoce prefijos y da prioridad a los identificadores exactos.</p>' +
      '<div class="suggestion-row">' +
        '<span class="quick-label">Búsquedas rápidas</span>' +
        '<button class="suggestion-chip" type="button" data-search-suggestion="auditoría">auditoría</button>' +
        '<button class="suggestion-chip" type="button" data-search-suggestion="control de acceso">control de acceso</button>' +
        '<button class="suggestion-chip" type="button" data-search-suggestion="autenticación">autenticación</button>' +
        '<button class="suggestion-chip" type="button" data-search-suggestion="residual">residual</button>' +
        '<button class="suggestion-chip" type="button" data-search-suggestion="FAU_ARP.1">FAU_ARP.1</button>' +
      '</div>' +
      '<div class="search-start-classes">' +
        '<p class="eyebrow">O empieza por una clase</p>' +
        '<div class="mini-class-grid">' +
          d.classes.map(function (cls) {
            return '<a class="mini-class" href="' + e(cls.href) + '" style="' + classStyle(cls) + '">' +
              '<span>' + e(cls.id) + '</span><strong>' + e(cls.name) + '</strong>' + icon('arrow-right') +
            '</a>';
          }).join('') +
        '</div>' +
      '</div>' +
    '</div>';
  }

  function renderSearchResults(result, query, type, classId) {
    if (!query) return renderSearchStart();

    if (!result.results.length) {
      return '<div class="empty-state">' +
        '<div class="empty-state-mark">' + icon('search') + '</div>' +
        '<h2>Sin resultados para «' + e(query) + '»</h2>' +
        '<p>Prueba con menos palabras, revisa la escritura o busca por un identificador como <strong>FAU_ARP.1</strong>. También puedes quitar los filtros activos.</p>' +
        '<div class="empty-actions">' +
          (type !== 'all' || classId ? '<button class="button button-ghost" type="button" data-action="clear-search-filters">Quitar filtros</button>' : '') +
          '<a class="button button-primary" href="#/catalogo">Explorar el catálogo ' + icon('arrow-right') + '</a>' +
        '</div>' +
      '</div>';
    }

    return '<div class="results-head">' +
      '<p><strong>' + e(utils.formatNumber(result.total)) + '</strong> ' + utils.pluralize(result.total, 'resultado', 'resultados') + ' para «' + e(query) + '»</p>' +
      '<span class="results-note">' + icon('compass') + ' Índice local · búsqueda tolerante a tildes</span>' +
    '</div>' +
    '<div class="results-list">' + result.results.map(function (item) {
      return renderSearchResult(item, query);
    }).join('') + '</div>';
  }

  function renderSearchPage(query, type, classId) {
    const d = data();
    const normalizedType = TYPE_LABELS[type] ? type : 'all';
    const normalizedClass = classId && d.maps.classById.has(classId) ? classId : '';
    const result = CC.search.search(query, { type: normalizedType, classId: normalizedClass });
    const facets = result.facets;
    const hasFilter = normalizedType !== 'all' || Boolean(normalizedClass);

    return '<section class="search-page-head">' +
      '<div class="container">' +
        '<p class="eyebrow">Buscador</p>' +
        '<h1>Encuentra el requisito exacto.</h1>' +
        '<form class="search-form-large" data-search-form role="search">' +
          '<label class="sr-only" for="search-input">Buscar en Criterios Comunes</label>' +
          '<div class="search-field">' +
            icon('search') +
            '<input id="search-input" name="q" type="search" value="' + e(query) + '" placeholder="Busca por ID, clase, familia, componente o texto…" autocomplete="off" spellcheck="false" data-live-search>' +
            '<button class="clear-search" type="button" data-action="clear-search" aria-label="Borrar búsqueda"' + (query ? '' : ' hidden') + '>' + icon('close') + '</button>' +
            '<button class="button button-primary" type="submit">Buscar ' + icon('arrow-right') + '</button>' +
          '</div>' +
        '</form>' +
      '</div>' +
    '</section>' +
    '<div class="container search-layout' + (query ? '' : ' is-query-empty') + '">' +
      '<aside class="search-filters" aria-label="Filtros de búsqueda">' +
        '<div class="filter-group">' +
          '<p class="filter-title">Tipo de resultado</p>' +
          '<div class="filter-chips">' +
            TYPE_ORDER.map(function (key) {
              const count = key === 'all' ? facets.all : facets[key];
              return '<button class="filter-chip' + (normalizedType === key ? ' is-active' : '') + '" type="button" data-search-type="' + key + '">' +
                e(TYPE_LABELS[key]) + '<span>' + count + '</span>' +
              '</button>';
            }).join('') +
          '</div>' +
        '</div>' +
        '<div class="filter-group">' +
          '<label class="filter-title" for="search-class">Clase</label>' +
          '<div class="select-wrap">' +
            '<select id="search-class" data-search-class>' +
              '<option value="">Todas las clases</option>' +
              d.classes.map(function (cls) {
                return '<option value="' + e(cls.id) + '"' + (normalizedClass === cls.id ? ' selected' : '') + '>' + e(cls.id) + ' · ' + e(cls.name) + '</option>';
              }).join('') +
            '</select>' +
            icon('chevron-down') +
          '</div>' +
        '</div>' +
        '<button class="text-button filter-reset" type="button" data-action="clear-search-filters"' + (hasFilter ? '' : ' hidden') + '>' + icon('reset') + ' Limpiar filtros</button>' +
        '<div class="filter-note">' + icon('info') + '<p>Los filtros no modifican el texto de tu búsqueda. Se aplican sobre los resultados del índice local.</p></div>' +
      '</aside>' +
      '<div class="search-results" id="search-results" aria-live="polite">' +
        renderSearchResults(result, query, normalizedType, normalizedClass) +
      '</div>' +
    '</div>';
  }

  function renderElementBlocks(blocks) {
    return blocks.map(function (block) {
      if (block.type === 'list') {
        const tag = block.ordered ? 'ol' : 'ul';
        return '<' + tag + ' class="cc-list">' + block.items.map(function (item) {
          return '<li>' + utils.formatCC(item) + '</li>';
        }).join('') + '</' + tag + '>';
      }
      return '<p>' + utils.formatCC(block.text) + '</p>';
    }).join('');
  }

  function renderElementCard(element, selected) {
    return '<article class="element-card' + (selected ? ' is-selected' : '') + '" id="elemento-' + e(element.id) + '" data-element-card="' + e(element.id) + '">' +
      '<header class="element-head">' +
        '<span class="element-id">' + e(element.id) + '</span>' +
        '<button class="element-copy" type="button" data-action="copy-id" data-id="' + e(element.id) + '" aria-label="Copiar ' + e(element.id) + '">' + icon('copy') + '<span>Copiar ID</span></button>' +
      '</header>' +
      '<div class="element-content">' + renderElementBlocks(element.blocks) + '</div>' +
    '</article>';
  }

  function renderElementRail(component, selectedId) {
    const count = component.elements.length;
    const items = component.elements.map(function (element, index) {
      const active = element.id === selectedId;
      return '<div class="element-rail-row' + (active ? ' is-active' : '') + '">' +
        '<button class="element-rail-select" type="button" data-element-select="' + e(element.id) + '"' + (active ? ' aria-current="true"' : '') + '>' +
          '<span class="element-rail-index">' + padNumber(index + 1) + '</span>' +
          '<span class="element-rail-id">' + e(element.id) + '</span>' +
        '</button>' +
        '<button class="element-rail-copy" type="button" data-action="copy-id" data-id="' + e(element.id) + '" title="Copiar ID" aria-label="Copiar ' + e(element.id) + '">' + icon('copy') + '</button>' +
      '</div>';
    }).join('');

    return '<aside class="element-rail" aria-label="Elementos del componente">' +
      '<div class="element-rail-head"><p class="eyebrow">Elementos</p><span class="element-rail-count">' + count + '</span></div>' +
      (count ? '<div class="element-rail-list">' + items + '</div>' : '<p class="element-rail-empty">Sin elementos cargados.</p>') +
    '</aside>';
  }

  function renderSupportSections(component) {
    return '<div class="detail-support">' +
      '<section class="detail-section" aria-labelledby="gestion-title">' +
        '<div class="detail-section-head"><div><p class="eyebrow">FMT</p><h2 id="gestion-title">Gestión</h2></div></div>' +
        '<div class="info-card">' +
          (component.management && component.management.length
            ? '<ul class="plain-list">' + component.management.map(function (item) { return '<li>' + e(item) + '</li>'; }).join('') + '</ul>'
            : '<p>No se prevén actividades de gestión para este componente.</p>') +
        '</div>' +
      '</section>' +
      '<section class="detail-section" aria-labelledby="auditoria-title">' +
        '<div class="detail-section-head"><div><p class="eyebrow">FAU_GEN</p><h2 id="auditoria-title">Auditoría</h2></div></div>' +
        '<div class="info-card">' +
          (component.audit && component.audit.length
            ? '<ul class="audit-list">' + component.audit.map(function (item) {
              return '<li><span class="level-pill level-' + e(utils.normalizeText(item.level).replace(/\s+/g, '-')) + '">' + e(item.level) + '</span><span>' + e(item.text) + '</span></li>';
            }).join('') + '</ul>'
            : '<p>No se prevén eventos auditables para este componente.</p>') +
        '</div>' +
      '</section>' +
    '</div>';
  }

  function renderComponentPage(component, elementId) {
    if (!component) return renderNotFound();

    const cls = classByComponent(component);
    const family = familyByComponent(component);
    const requestedElement = elementId && component.elements.some(function (element) { return element.id === elementId; }) ? elementId : '';
    const selectedId = requestedElement || (component.elements[0] ? component.elements[0].id : '');

    return '<section class="detail-hero" style="' + classStyle(cls) + '">' +
      '<div class="container">' +
        breadcrumbs([
          { label: 'Inicio', href: '#/' },
          { label: 'Catálogo', href: '#/catalogo' },
          { label: cls.id, href: cls.href },
          { label: family.id, href: family.href },
          { label: component.id, href: component.href }
        ]) +
        '<div class="detail-hero-grid">' +
          '<div class="detail-hero-copy">' +
            '<p class="eyebrow">' + classBadge(cls) + ' ' + e(cls.id) + ' · ' + e(family.id) + ' · Componente funcional</p>' +
            '<div class="detail-id-row"><span class="detail-id">' + e(component.id) + '</span>' +
              (component.available ? '<span class="status-pill status-complete">' + icon('check-circle') + ' Ficha completa</span>' : '') +
            '</div>' +
            '<h1>' + e(component.name) + '</h1>' +
            '<p class="detail-summary">' + (component.summary ? e(component.summary) : 'Sin resumen disponible.') + '</p>' +
            '<div class="detail-actions">' +
              '<button class="button button-ghost" type="button" data-action="copy-id" data-id="' + e(component.id) + '">' + icon('copy') + ' Copiar ID</button>' +
              '<button class="button button-ghost" type="button" data-action="print">' + icon('printer') + ' Imprimir</button>' +
            '</div>' +
          '</div>' +
          '<div class="detail-stamp" aria-hidden="true"><span>' + e(cls.id) + '</span><strong>' + e(family.id) + '</strong><small>' + e(component.id) + '</small></div>' +
        '</div>' +
      '</div>' +
    '</section>' +
    '<div class="container detail-layout detail-layout-elements" style="' + classStyle(cls) + '">' +
      renderElementRail(component, selectedId) +
      '<div class="detail-main element-viewer">' +
        '<div class="detail-section-head element-viewer-head">' +
          '<div><p class="eyebrow">Declaraciones normativas</p><h2>Elementos <span>' + component.elements.length + '</span></h2></div>' +
          '<span class="detail-section-note">' + e(component.id) + '</span>' +
        '</div>' +
        '<p class="element-legend">' + icon('info') + ' Las expresiones entre corchetes son operaciones de asignación o selección que se completan al aplicar el requisito.</p>' +
        (component.elements.length
          ? '<div class="element-list">' + component.elements.map(function (element) {
            return renderElementCard(element, element.id === selectedId);
          }).join('') + '</div>'
          : '<div class="info-card"><p>Este componente no tiene elementos cargados.</p></div>') +
      '</div>' +
      renderSupportSections(component) +
    '</div>';
  }

  function renderNotFound() {
    return '<section class="not-found">' +
      '<div class="container">' +
        '<p class="eyebrow">Error 404</p>' +
        '<h1>Esta página no existe.</h1>' +
        '<p>Puede que el enlace esté mal escrito o que el contenido todavía no forme parte de la muestra.</p>' +
        '<div class="not-found-actions">' +
          '<a class="button button-primary" href="#/">Volver al inicio ' + icon('arrow-right') + '</a>' +
          '<a class="button button-ghost" href="#/catalogo">Abrir el catálogo</a>' +
        '</div>' +
        '<div class="not-found-mark" aria-hidden="true">404</div>' +
      '</div>' +
    '</section>';
  }

  CC.views = {
    home: renderHome,
    catalog: renderCatalog,
    classPage: renderClassPage,
    search: renderSearchPage,
    searchResults: renderSearchResults,
    component: renderComponentPage,
    notFound: renderNotFound
  };
})(window);

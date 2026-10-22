/* Common Criteria — carga de datos, enrutamiento y comportamiento de la interfaz. */
(function (global) {
  'use strict';

  const CC = global.CC;
  const utils = CC.utils;
  const app = document.getElementById('app');
  const main = document.getElementById('contenido');

  let currentRoute = { name: 'home', route: null };
  let searchState = { q: '', type: 'all', classId: '' };
  let focusSearchOnRender = false;
  let dataLoadFailed = false;

  const scheduleLiveSearch = utils.debounce(runLiveSearch, 90);

  /* ------------------------------------------------------------------ */
  /* Datos                                                              */
  /* ------------------------------------------------------------------ */

  function normalizeData(raw) {
    if (!raw || !Array.isArray(raw.classes)) {
      throw new Error('El archivo de datos no tiene el formato esperado.');
    }

    const data = {
      meta: raw.meta || {},
      classes: raw.classes,
      families: [],
      components: [],
      elements: [],
      maps: {
        classById: new Map(),
        familyById: new Map(),
        componentById: new Map(),
        elementById: new Map()
      },
      stats: {}
    };

    data.classes.sort(function (a, b) {
      return Number(a.number) - Number(b.number);
    });

    data.classes.forEach(function (cls) {
      cls.number = Number(cls.number) || 0;
      cls.families = Array.isArray(cls.families) ? cls.families : [];
      cls.href = '#/clase/' + encodeURIComponent(cls.id);
      cls.familyCount = cls.families.length;
      cls.componentCount = 0;
      cls.completeCount = 0;
      cls.color = cls.color || '#b4432c';

      cls.families.forEach(function (family) {
        family.classId = cls.id;
        family.className = cls.name;
        family.classColor = cls.color;
        family.href = cls.href + '?familia=' + encodeURIComponent(family.id);
        family.components = Array.isArray(family.components) ? family.components : [];
        family.componentCount = family.components.length;
        family.completeCount = 0;

        family.components.forEach(function (component) {
          component.classId = cls.id;
          component.className = cls.name;
          component.classColor = cls.color;
          component.familyId = family.id;
          component.familyName = family.name;
          component.href = '#/componente/' + encodeURIComponent(component.id);
          component.available = component.available === true;
          component.summary = component.summary || '';
          component.elements = Array.isArray(component.elements) ? component.elements : [];
          component.management = Array.isArray(component.management) ? component.management : [];
          component.audit = Array.isArray(component.audit) ? component.audit : [];
          component.dependencies = Array.isArray(component.dependencies) ? component.dependencies : [];
          component.hierarchicalTo = Array.isArray(component.hierarchicalTo) ? component.hierarchicalTo : [];

          component.elements.forEach(function (element) {
            element.componentId = component.id;
            element.componentName = component.name;
            element.familyId = family.id;
            element.familyName = family.name;
            element.classId = cls.id;
            element.className = cls.name;
            element.classColor = cls.color;
            element.blocks = Array.isArray(element.blocks) ? element.blocks : [];
            element.href = component.href + '?elemento=' + encodeURIComponent(element.id);
            data.elements.push(element);
            data.maps.elementById.set(element.id, element);
          });

          cls.componentCount += 1;
          family.completeCount += component.available ? 1 : 0;
          cls.completeCount += component.available ? 1 : 0;
          data.components.push(component);
          data.maps.componentById.set(component.id, component);
        });

        data.families.push(family);
        data.maps.familyById.set(family.id, family);
      });

      data.maps.classById.set(cls.id, cls);
    });

    data.components.forEach(function (component, index) {
      component.index = index;
      component.prev = data.components[index - 1] || null;
      component.next = data.components[index + 1] || null;
    });

    data.stats = {
      classes: data.classes.length,
      families: data.families.length,
      components: data.components.length,
      elements: data.elements.length,
      completeComponents: data.components.filter(function (component) { return component.available; }).length
    };

    return data;
  }

  async function loadData() {
    const response = await fetch('data/cc.json', { cache: 'no-cache' });
    if (!response.ok) throw new Error('No se pudo leer data/cc.json (' + response.status + ').');
    const raw = await response.json();
    CC.data = normalizeData(raw);
    CC.search = new CC.SearchEngine(CC.data);
  }

  /* ------------------------------------------------------------------ */
  /* Rutas y render                                                     */
  /* ------------------------------------------------------------------ */

  function getRoute() {
    const hash = window.location.hash.startsWith('#') ? window.location.hash.slice(1) : window.location.hash;
    const raw = hash || '/';
    const split = raw.split('?');
    const path = split[0] || '/';
    const segments = path.split('/').filter(Boolean).map(function (segment) {
      try { return decodeURIComponent(segment); } catch (error) { return segment; }
    });

    return {
      raw: raw,
      segments: segments,
      params: new URLSearchParams(split[1] || '')
    };
  }

  function notFoundView() {
    return {
      name: 'notFound',
      html: CC.views.notFound(),
      title: 'Página no encontrada — Common Criteria',
      nav: null,
      announce: 'Página no encontrada'
    };
  }

  function resolveRoute(route) {
    const d = CC.data;
    if (!d) return null;

    const parts = route.segments;
    if (!parts.length) {
      return {
        name: 'home',
        html: CC.views.home(),
        title: 'Common Criteria — Explorador de criterios comunes',
        nav: 'home',
        announce: 'Inicio de Common Criteria'
      };
    }

    switch (parts[0]) {
      case 'catalogo':
        return {
          name: 'catalog',
          html: CC.views.catalog(),
          title: 'Catálogo — Common Criteria',
          nav: 'catalog',
          announce: 'Catálogo de clases'
        };

      case 'clase': {
        const cls = d.maps.classById.get(parts[1]);
        if (!cls) return notFoundView();
        const familyId = route.params.get('familia') || '';
        const family = familyId && cls.families.some(function (item) { return item.id === familyId; }) ? familyId : '';
        return {
          name: 'class',
          html: CC.views.classPage(cls, family),
          title: cls.id + ' · ' + cls.name + ' — Common Criteria',
          nav: 'catalog',
          announce: 'Clase ' + cls.id + ': ' + cls.name,
          familyId: family
        };
      }

      case 'componente': {
        const componentId = parts[1] ? parts[1].toUpperCase() : '';
        const component = d.maps.componentById.get(componentId);
        if (!component) return notFoundView();
        const elementId = route.params.get('elemento') || '';
        return {
          name: 'component',
          html: CC.views.component(component, elementId),
          title: component.id + ' · ' + component.name + ' — Common Criteria',
          nav: 'catalog',
          announce: 'Componente ' + component.id + ': ' + component.name,
          elementId: elementId
        };
      }

      case 'buscar': {
        const query = route.params.get('q') || '';
        const requestedType = route.params.get('tipo') || 'all';
        const type = ['all', 'class', 'family', 'component', 'element'].indexOf(requestedType) !== -1 ? requestedType : 'all';
        const requestedClass = route.params.get('clase') || '';
        const classId = requestedClass && d.maps.classById.has(requestedClass) ? requestedClass : '';
        searchState = { q: query, type: type, classId: classId };
        const result = CC.search.search(query, { type: type, classId: classId });
        return {
          name: 'search',
          html: CC.views.search(query, type, classId),
          title: query ? 'Búsqueda: ' + query + ' — Common Criteria' : 'Buscador — Common Criteria',
          nav: null,
          announce: query ? 'Búsqueda: ' + query + '. ' + result.total + ' resultados.' : 'Buscador'
        };
      }

      default:
        return notFoundView();
    }
  }

  function updateNavigation(activeName) {
    document.querySelectorAll('[data-nav]').forEach(function (link) {
      const active = link.dataset.nav === activeName;
      link.classList.toggle('is-active', active);
      if (active) link.setAttribute('aria-current', 'page');
      else link.removeAttribute('aria-current');
    });
  }

  function renderRoute(options) {
    const settings = options || {};
    if (!CC.data) {
      if (dataLoadFailed) renderDataError();
      return;
    }

    const route = getRoute();
    const view = resolveRoute(route);
    if (!view) {
      renderDataError();
      return;
    }

    currentRoute = { name: view.name, route: route };

    app.innerHTML = view.html;
    document.title = view.title;
    updateNavigation(view.nav);
    closeMenu();

    if (!settings.preserveScroll) window.scrollTo({ top: 0, left: 0, behavior: 'auto' });

    const announcer = document.getElementById('route-announcer');
    if (announcer) announcer.textContent = view.announce || '';

    if (settings.focusMain) {
      requestAnimationFrame(function () {
        main.focus({ preventScroll: true });
      });
    }

    if (view.name === 'search' && focusSearchOnRender) {
      focusSearchOnRender = false;
      requestAnimationFrame(function () {
        const input = document.getElementById('search-input');
        if (input) input.focus();
      });
    }

    if (view.name === 'component' && view.elementId) {
      setTimeout(function () {
        scrollToElement(view.elementId);
      }, 80);
    }

    if (view.name === 'class' && view.familyId) {
      setTimeout(function () {
        scrollToFamily(view.familyId);
      }, 80);
    }
  }

  function renderDataError(error) {
    dataLoadFailed = true;
    const isFile = window.location.protocol === 'file:';
    const message = isFile
      ? '<p>Estás abriendo <code>index.html</code> directamente desde el disco. El navegador bloquea la carga del archivo de datos por seguridad.</p>' +
        '<p>Inicia un servidor local desde la carpeta del proyecto:</p>' +
        '<pre><code>python -m http.server 8000</code></pre>' +
        '<p>Después abre <a href="http://localhost:8000">http://localhost:8000</a> en tu navegador.</p>'
      : '<p>No se pudo cargar <code>data/cc.json</code>. Revisa que el archivo exista, que la ruta sea correcta y que el sitio se esté sirviendo por HTTP.</p>';

    app.innerHTML = '<section class="data-error">' +
      '<div class="container">' +
        '<span class="data-error-mark">' + utils.icon('alert') + '</span>' +
        '<p class="eyebrow">Error de carga</p>' +
        '<h1>No se pudo abrir el catálogo</h1>' +
        message +
        '<div class="data-error-actions">' +
          '<button class="button button-primary" type="button" data-action="reload">Reintentar</button>' +
          '<a class="button button-ghost" href="#/catalogo">Abrir el catálogo</a>' +
        '</div>' +
      '</div>' +
    '</section>';

    document.title = 'Error de carga — Common Criteria';
    console.error('[Common Criteria] Error al cargar los datos:', error);
  }

  function scrollToElement(id) {
    const target = document.getElementById('elemento-' + id);
    if (!target) return;
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    target.classList.add('is-highlighted');
    setTimeout(function () {
      target.classList.remove('is-highlighted');
    }, 2200);
  }

  function scrollToFamily(id) {
    const target = document.getElementById('familia-' + id);
    if (!target) return;
    target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    target.classList.add('is-highlighted');
    setTimeout(function () {
      target.classList.remove('is-highlighted');
    }, 2200);
  }

  function selectComponentElement(id) {
    if (!id) return;

    const target = document.getElementById('elemento-' + id);
    if (!target) return;

    document.querySelectorAll('[data-element-card]').forEach(function (card) {
      card.classList.toggle('is-selected', card.dataset.elementCard === id);
    });

    document.querySelectorAll('[data-element-select]').forEach(function (button) {
      const active = button.dataset.elementSelect === id;
      button.classList.toggle('is-active', active);
      if (active) button.setAttribute('aria-current', 'true');
      else button.removeAttribute('aria-current');
      const row = button.closest('.element-rail-row');
      if (row) row.classList.toggle('is-active', active);
    });

    scrollToElement(id);

    if (currentRoute.route && currentRoute.route.segments && currentRoute.route.segments[0] === 'componente') {
      const componentId = currentRoute.route.segments[1];
      const hash = '#/componente/' + encodeURIComponent(componentId) + '?elemento=' + encodeURIComponent(id);
      if (window.location.hash !== hash) history.replaceState(null, '', hash);
    }

    const announcer = document.getElementById('route-announcer');
    if (announcer) announcer.textContent = 'Elemento ' + id;
  }

  /* ------------------------------------------------------------------ */
  /* Búsqueda en vivo                                                   */
  /* ------------------------------------------------------------------ */

  function buildSearchHash(query, type, classId) {
    const params = new URLSearchParams();
    if (query) params.set('q', query);
    if (type && type !== 'all') params.set('tipo', type);
    if (classId) params.set('clase', classId);
    const queryString = params.toString();
    return '#/buscar' + (queryString ? '?' + queryString : '');
  }

  function updateSearchURL(query, type, classId) {
    const hash = buildSearchHash(query, type, classId);
    if (window.location.hash !== hash) {
      history.replaceState(null, '', hash);
    }
  }

  function updateClearButton(query) {
    const clear = document.querySelector('[data-action="clear-search"]');
    if (clear) clear.hidden = !query;
  }

  function updateFacets(result) {
    document.querySelectorAll('[data-search-type]').forEach(function (button) {
      const key = button.dataset.searchType;
      const count = key === 'all' ? result.facets.all : result.facets[key];
      const badge = button.querySelector('span');
      if (badge) badge.textContent = String(count);
    });

    document.querySelectorAll('[data-search-type]').forEach(function (button) {
      button.classList.toggle('is-active', button.dataset.searchType === searchState.type);
    });

    const reset = document.querySelector('.filter-reset');
    if (reset) reset.hidden = searchState.type === 'all' && !searchState.classId;
  }

  function runLiveSearch() {
    if (!CC.data || currentRoute.name !== 'search') return;
    const input = document.querySelector('[data-live-search]');
    if (!input) return;

    const query = input.value;
    searchState.q = query;
    const result = CC.search.search(query, { type: searchState.type, classId: searchState.classId });
    const results = document.getElementById('search-results');
    const layout = document.querySelector('.search-layout');

    if (layout) layout.classList.toggle('is-query-empty', !query.trim());

    if (results) {
      results.innerHTML = CC.views.searchResults(result, query, searchState.type, searchState.classId);
    }

    updateFacets(result);
    updateClearButton(query);
    updateSearchURL(query, searchState.type, searchState.classId);
  }

  /* ------------------------------------------------------------------ */
  /* Menú móvil y utilidades de shell                                   */
  /* ------------------------------------------------------------------ */

  function closeMenu() {
    document.body.classList.remove('menu-open');
    const button = document.getElementById('menu-toggle');
    if (button) {
      button.setAttribute('aria-expanded', 'false');
      button.setAttribute('aria-label', 'Abrir el menú');
    }
  }

  function toggleMenu() {
    const open = !document.body.classList.contains('menu-open');
    document.body.classList.toggle('menu-open', open);
    const button = document.getElementById('menu-toggle');
    if (button) {
      button.setAttribute('aria-expanded', String(open));
      button.setAttribute('aria-label', open ? 'Cerrar el menú' : 'Abrir el menú');
    }
  }

  function isEditable(target) {
    if (!target) return false;
    const tag = target.tagName;
    return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || target.isContentEditable;
  }

  function focusSearchInput() {
    const input = document.getElementById('search-input');
    if (input) input.focus();
  }

  function openSearch() {
    if (!CC.data) return;
    closeMenu();
    if (currentRoute.name === 'search') {
      focusSearchInput();
      return;
    }
    focusSearchOnRender = true;
    navigate('#/buscar');
  }

  function navigate(hash) {
    if (window.location.hash === hash) {
      renderRoute({ focusMain: true });
    } else {
      window.location.hash = hash;
    }
  }

  function bindShellEvents() {
    const searchTrigger = document.getElementById('search-trigger');
    if (searchTrigger) searchTrigger.addEventListener('click', openSearch);

    const menuToggle = document.getElementById('menu-toggle');
    if (menuToggle) menuToggle.addEventListener('click', toggleMenu);

    document.getElementById('main-nav').addEventListener('click', function (event) {
      if (event.target.closest('a')) closeMenu();
    });

    window.addEventListener('hashchange', function () {
      renderRoute({ focusMain: true });
    });

    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') {
        closeMenu();
      }

      const command = (event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k';
      const slash = event.key === '/' && !isEditable(event.target) && !event.ctrlKey && !event.metaKey && !event.altKey;

      if (command || slash) {
        event.preventDefault();
        openSearch();
      }
    });

    if (window.matchMedia) {
      const media = window.matchMedia('(max-width: 900px)');
      const onChange = function () { closeMenu(); };
      if (typeof media.addEventListener === 'function') media.addEventListener('change', onChange);
      else if (typeof media.addListener === 'function') media.addListener(onChange);
    }
  }

  /* ------------------------------------------------------------------ */
  /* Eventos globales                                                   */
  /* ------------------------------------------------------------------ */

  function bindGlobalEvents() {
    document.addEventListener('click', function (event) {
      const actionElement = event.target.closest('[data-action]');
      if (actionElement) {
        const action = actionElement.dataset.action;
        const id = actionElement.dataset.id;

        if (action === 'copy-id' && id) {
          utils.copyText(id).then(function () {
            CC.toast('ID copiado: ' + id);
          }).catch(function () {
            CC.toast('No se pudo copiar el ID');
          });
          return;
        }

        if (action === 'print') {
          window.print();
          return;
        }

        if (action === 'reload') {
          window.location.reload();
          return;
        }

        if (action === 'clear-search') {
          const input = document.querySelector('[data-live-search]');
          if (input) {
            input.value = '';
            input.focus();
            runLiveSearch();
          }
          return;
        }

        if (action === 'clear-search-filters') {
          if (currentRoute.name !== 'search') return;
          searchState.type = 'all';
          searchState.classId = '';
          const select = document.querySelector('[data-search-class]');
          if (select) select.value = '';
          updateFacets(CC.search.search(searchState.q, { type: 'all', classId: '' }));
          runLiveSearch();
          return;
        }
      }

      const elementSelect = event.target.closest('[data-element-select]');
      if (elementSelect && currentRoute.name === 'component') {
        selectComponentElement(elementSelect.dataset.elementSelect);
        return;
      }

      const typeButton = event.target.closest('[data-search-type]');
      if (typeButton && currentRoute.name === 'search') {
        searchState.type = typeButton.dataset.searchType;
        document.querySelectorAll('[data-search-type]').forEach(function (button) {
          button.classList.toggle('is-active', button === typeButton);
        });
        runLiveSearch();
        return;
      }

      const suggestion = event.target.closest('[data-search-suggestion]');
      if (suggestion && currentRoute.name === 'search') {
        const input = document.querySelector('[data-live-search]');
        if (input) {
          input.value = suggestion.dataset.searchSuggestion || '';
          input.focus();
          runLiveSearch();
        }
        return;
      }

      if (event.target.closest('.main-nav a, .brand')) closeMenu();
    });

    document.addEventListener('submit', function (event) {
      const searchForm = event.target.closest('form[data-search-form]');
      if (!searchForm) return;

      event.preventDefault();
      const input = searchForm.querySelector('input[name="q"]');
      const query = input ? input.value.trim() : '';
      let type = 'all';
      let classId = '';

      if (currentRoute.name === 'search') {
        type = searchState.type;
        classId = searchState.classId;
      }

      focusSearchOnRender = true;
      navigate(buildSearchHash(query, type, classId));
    });

    document.addEventListener('input', function (event) {
      if (!event.target.matches('[data-live-search]')) return;
      updateClearButton(event.target.value);
      scheduleLiveSearch();
    });

    document.addEventListener('change', function (event) {
      if (!event.target.matches('[data-search-class]') || currentRoute.name !== 'search') return;
      searchState.classId = event.target.value;
      runLiveSearch();
    });
  }

  /* ------------------------------------------------------------------ */
  /* Inicio                                                             */
  /* ------------------------------------------------------------------ */

  async function init() {
    CC.theme.init();
    bindShellEvents();
    bindGlobalEvents();

    const year = document.getElementById('footer-year');
    if (year) year.textContent = String(new Date().getFullYear());

    try {
      await loadData();
      renderRoute();
    } catch (error) {
      renderDataError(error);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})(window);

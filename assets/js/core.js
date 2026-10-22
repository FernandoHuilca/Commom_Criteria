/* Common Criteria — utilidades base, almacenamiento local y tema. */
(function (global) {
  'use strict';

  const CC = global.CC = global.CC || {};

  const HTML_ESCAPES = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  };

  const ACCENT_CLASSES = {
    a: '[aáàäâ]',
    e: '[eéèëê]',
    i: '[iíìïî]',
    o: '[oóòöô]',
    u: '[uúùüû]',
    n: '[nñ]',
    c: '[cç]'
  };

  const STOPWORDS = new Set([
    'a', 'al', 'algo', 'algunas', 'algunos', 'ante', 'antes', 'como', 'con', 'contra',
    'cual', 'cuales', 'cuando', 'de', 'del', 'desde', 'donde', 'durante', 'e', 'el',
    'ella', 'ellas', 'ellos', 'en', 'entre', 'era', 'es', 'esa', 'esas', 'ese', 'eso',
    'esos', 'esta', 'estas', 'este', 'esto', 'estos', 'fue', 'ha', 'hasta', 'hay',
    'la', 'las', 'le', 'les', 'lo', 'los', 'mas', 'más', 'me', 'mi', 'mis', 'muy',
    'no', 'nos', 'o', 'otra', 'otras', 'otro', 'otros', 'para', 'pero', 'poco', 'por',
    'porque', 'que', 'quien', 'quienes', 'se', 'sea', 'ser', 'si', 'sin', 'sobre',
    'son', 'su', 'sus', 'tambien', 'también', 'tanto', 'te', 'tiene', 'tienen', 'todo',
    'todos', 'tu', 'tus', 'un', 'una', 'unas', 'uno', 'unos', 'y', 'ya'
  ]);

  function queryTokens(query) {
    const seen = Object.create(null);
    return String(query || '')
      .split(/\s+/)
      .map(function (token) { return token.replace(/^[^\wáéíóúüñ]+|[^\wáéíóúüñ]+$/gi, ''); })
      .filter(function (token) {
        const normalized = utils.normalizeText(token);
        if (token.length < 2 || STOPWORDS.has(normalized)) return false;
        if (seen[normalized]) return false;
        seen[normalized] = true;
        return true;
      })
      .map(function (token) { return utils.normalizeText(token); });
  }

  const ABBREVIATIONS = {
    TSF: 'Funcionalidad de seguridad de la TOE',
    TOE: 'Objetivo de evaluación',
    SFR: 'Requisito funcional de seguridad',
    SFP: 'Política de seguridad funcional',
    PP: 'Perfil de protección',
    'PP-Module': 'Módulo de perfil de protección',
    ST: 'Especificación del objetivo de seguridad',
    TSFI: 'Interfaz de la TSF'
  };

  const utils = {
    escapeHtml(value) {
      return String(value == null ? '' : value).replace(/[&<>"']/g, function (character) {
        return HTML_ESCAPES[character];
      });
    },

    escapeRegExp(value) {
      return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    },

    normalizeText(value) {
      return String(value == null ? '' : value)
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .toLowerCase()
        .trim();
    },

    slug(value) {
      return utils.normalizeText(value)
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '');
    },

    icon(name, className) {
      return '<svg class="icon ' + (className || '') + '" aria-hidden="true"><use href="#icon-' + name + '"></use></svg>';
    },

    pluralize(count, singular, plural) {
      return count === 1 ? singular : (plural || singular + 's');
    },

    debounce(fn, wait) {
      let timer = null;
      return function () {
        const context = this;
        const args = arguments;
        clearTimeout(timer);
        timer = setTimeout(function () {
          fn.apply(context, args);
        }, wait);
      };
    },

    copyText(text) {
      if (navigator.clipboard && window.isSecureContext) {
        return navigator.clipboard.writeText(text);
      }

      return new Promise(function (resolve, reject) {
        const area = document.createElement('textarea');
        area.value = text;
        area.setAttribute('readonly', '');
        area.style.position = 'fixed';
        area.style.opacity = '0';
        document.body.appendChild(area);
        area.select();

        try {
          const ok = document.execCommand('copy');
          document.body.removeChild(area);
          ok ? resolve() : reject(new Error('No se pudo copiar'));
        } catch (error) {
          document.body.removeChild(area);
          reject(error);
        }
      });
    },

    accentPattern(token) {
      return String(token).split('').map(function (character) {
        return ACCENT_CLASSES[character] || utils.escapeRegExp(character);
      }).join('');
    },

    highlight(text, query) {
      const tokens = queryTokens(query);

      if (!tokens.length) return utils.escapeHtml(text);

      const patterns = tokens.map(function (token) {
        return utils.accentPattern(token);
      });

      if (!patterns.length) return utils.escapeHtml(text);

      let regex;
      try {
        regex = new RegExp('(' + patterns.join('|') + ')', 'gi');
      } catch (error) {
        return utils.escapeHtml(text);
      }

      const source = String(text == null ? '' : text);
      let result = '';
      let lastIndex = 0;
      let match;

      while ((match = regex.exec(source)) !== null) {
        result += utils.escapeHtml(source.slice(lastIndex, match.index));
        result += '<mark>' + utils.escapeHtml(match[0]) + '</mark>';
        lastIndex = match.index + match[0].length;

        if (match[0].length === 0) regex.lastIndex += 1;
      }

      result += utils.escapeHtml(source.slice(lastIndex));
      return result;
    },

    formatCC(text) {
      let html = utils.escapeHtml(text);

      html = html.replace(/\b(TSFI|TSF|TOE|SFR|SFP|PP-Module|PP|ST)\b/g, function (match) {
        const title = ABBREVIATIONS[match] || '';
        return '<abbr title="' + utils.escapeHtml(title) + '">' + match + '</abbr>';
      });

      html = html.replace(/\[((?:asignaci[oó]n|selecci[oó]n|refinamiento)[^\]]*)\]/gi, function (match, inner) {
        return '<span class="cc-operation" title="Operación de Criterios Comunes que debe completarse al aplicar el requisito">[' + inner + ']</span>';
      });

      return html;
    },

    makeSnippet(text, query, maxLength) {
      const source = String(text == null ? '' : text).replace(/\s+/g, ' ').trim();
      const limit = maxLength || 190;
      if (!source) return '';

      const tokens = queryTokens(query);

      let start = 0;

      if (tokens.length) {
        try {
          const pattern = tokens.map(function (token) {
            return utils.accentPattern(token);
          }).join('|');
          const match = new RegExp(pattern, 'i').exec(source);
          if (match) start = Math.max(0, match.index - Math.floor(limit * 0.35));
        } catch (error) {
          start = 0;
        }
      }

      let snippet = source.slice(start, start + limit);
      if (start > 0) snippet = '… ' + snippet;
      if (start + limit < source.length) snippet += ' …';
      return snippet;
    },

    formatNumber(value) {
      return new Intl.NumberFormat('es-EC').format(value);
    }
  };

  const store = (function () {
    const KEYS = {
      favorites: 'atlascc.favorites.v1',
      studied: 'atlascc.studied.v1',
      notes: 'atlascc.notes.v1'
    };

    function readJSON(key, fallback) {
      try {
        const raw = localStorage.getItem(key);
        return raw ? JSON.parse(raw) : fallback;
      } catch (error) {
        return fallback;
      }
    }

    function writeJSON(key, value) {
      try {
        localStorage.setItem(key, JSON.stringify(value));
      } catch (error) {
        /* El almacenamiento puede estar bloqueado en modo privado. */
      }
    }

    function uniqueArray(value) {
      return Array.isArray(value) ? Array.from(new Set(value.filter(function (item) {
        return typeof item === 'string' && item.length > 0;
      }))) : [];
    }

    function emitChange() {
      document.dispatchEvent(new CustomEvent('cc:storechange'));
    }

    function getFavorites() {
      return uniqueArray(readJSON(KEYS.favorites, []));
    }

    function isFavorite(id) {
      return getFavorites().indexOf(id) !== -1;
    }

    function toggleFavorite(id) {
      const favorites = getFavorites();
      const index = favorites.indexOf(id);
      if (index === -1) favorites.push(id);
      else favorites.splice(index, 1);
      writeJSON(KEYS.favorites, favorites);
      emitChange();
      return index === -1;
    }

    function getStudied() {
      return uniqueArray(readJSON(KEYS.studied, []));
    }

    function isStudied(id) {
      return getStudied().indexOf(id) !== -1;
    }

    function toggleStudied(id) {
      const studied = getStudied();
      const index = studied.indexOf(id);
      if (index === -1) studied.push(id);
      else studied.splice(index, 1);
      writeJSON(KEYS.studied, studied);
      emitChange();
      return index === -1;
    }

    function getNotes() {
      const notes = readJSON(KEYS.notes, {});
      return notes && typeof notes === 'object' && !Array.isArray(notes) ? notes : {};
    }

    function getNote(id) {
      return getNotes()[id] || '';
    }

    function setNote(id, text) {
      const notes = getNotes();
      const clean = String(text || '');
      if (clean.trim()) notes[id] = clean;
      else delete notes[id];
      writeJSON(KEYS.notes, notes);
    }

    function clearProgress() {
      try {
        localStorage.removeItem(KEYS.favorites);
        localStorage.removeItem(KEYS.studied);
        localStorage.removeItem(KEYS.notes);
      } catch (error) {
        /* Sin acción. */
      }
      emitChange();
    }

    return {
      getFavorites,
      isFavorite,
      toggleFavorite,
      getStudied,
      isStudied,
      toggleStudied,
      getNotes,
      getNote,
      setNote,
      clearProgress
    };
  })();

  const theme = (function () {
    const THEME_KEY = 'atlascc.theme';

    function getTheme() {
      return document.documentElement.dataset.theme === 'dark' ? 'dark' : 'light';
    }

    function apply(themeName, persist) {
      const chosen = themeName === 'dark' ? 'dark' : 'light';
      document.documentElement.dataset.theme = chosen;

      const meta = document.querySelector('meta[name="theme-color"]');
      if (meta) meta.setAttribute('content', chosen === 'dark' ? '#0e1110' : '#f4f0e7');

      const button = document.getElementById('theme-toggle');
      if (button) {
        const isDark = chosen === 'dark';
        button.setAttribute('aria-pressed', String(isDark));
        button.setAttribute('aria-label', isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro');
        button.setAttribute('title', isDark ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro');
      }

      if (persist) {
        try {
          localStorage.setItem(THEME_KEY, chosen);
        } catch (error) {
          /* Sin acción. */
        }
      }
    }

    function init() {
      apply(getTheme(), false);

      const button = document.getElementById('theme-toggle');
      if (button) {
        button.addEventListener('click', function () {
          apply(getTheme() === 'dark' ? 'light' : 'dark', true);
        });
      }

      const media = window.matchMedia('(prefers-color-scheme: dark)');
      const onChange = function (event) {
        let hasPreference = false;
        try {
          hasPreference = Boolean(localStorage.getItem(THEME_KEY));
        } catch (error) {
          hasPreference = false;
        }
        if (!hasPreference) apply(event.matches ? 'dark' : 'light', false);
      };

      if (typeof media.addEventListener === 'function') media.addEventListener('change', onChange);
      else if (typeof media.addListener === 'function') media.addListener(onChange);
    }

    return { init, getTheme, apply };
  })();

  let toastTimer = null;

  function toast(message) {
    const element = document.getElementById('toast');
    if (!element) return;
    element.textContent = message;
    element.classList.add('is-visible');
    clearTimeout(toastTimer);
    toastTimer = setTimeout(function () {
      element.classList.remove('is-visible');
    }, 2600);
  }

  CC.utils = utils;
  CC.store = store;
  CC.theme = theme;
  CC.toast = toast;
})(window);

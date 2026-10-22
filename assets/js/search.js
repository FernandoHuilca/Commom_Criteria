/* Common Criteria — índice y motor de búsqueda en el navegador. */
(function (global) {
  'use strict';

  const CC = global.CC;
  const utils = CC.utils;

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

  const KIND_RANK = {
    component: 0,
    family: 1,
    class: 2,
    element: 3
  };

  const KIND_LABEL = {
    class: 'Clase',
    family: 'Familia',
    component: 'Componente',
    element: 'Elemento'
  };

  function tokenize(text) {
    return utils.normalizeText(text)
      .replace(/[^a-z0-9]+/g, ' ')
      .split(' ')
      .filter(function (token) {
        return token.length > 1 || /^\d$/.test(token);
      });
  }

  function uniqueTokens(text) {
    return Array.from(new Set(tokenize(text)));
  }

  function isIdQuery(query) {
    return /^[a-z]{3}(_[a-z]{3})?(\.\d+){0,2}$/i.test(String(query).trim());
  }

  class SearchEngine {
    constructor(data) {
      this.data = data;
      this.docs = [];
      this.docById = new Map();
      this.postings = new Map();
      this.vocabulary = new Set();
      this.build();
      this.vocabularyList = Array.from(this.vocabulary).sort();
    }

    addPosting(term, docIndex, weight) {
      if (!term) return;
      let bucket = this.postings.get(term);
      if (!bucket) {
        bucket = new Map();
        this.postings.set(term, bucket);
        this.vocabulary.add(term);
      }
      bucket.set(docIndex, (bucket.get(docIndex) || 0) + weight);
    }

    addField(docIndex, text, weight) {
      if (!text) return;
      uniqueTokens(text).forEach((term) => {
        this.addPosting(term, docIndex, weight);
      });
    }

    addDoc(doc) {
      const index = this.docs.length;
      doc._index = index;
      doc._idNorm = utils.normalizeText(doc.id);
      doc._titleNorm = utils.normalizeText(doc.title);
      doc._bodyNorm = utils.normalizeText(doc.body);

      this.docs.push(doc);
      if (doc.id && !this.docById.has(doc.id.toUpperCase())) {
        this.docById.set(doc.id.toUpperCase(), doc);
      }

      this.addField(index, doc.id, 18);
      this.addField(index, doc.id.replace(/[._]/g, ''), 22);
      this.addField(index, doc.title, 10);
      this.addField(index, doc.context, 4);
      this.addField(index, doc.body, 2);
      if (doc.keywords) this.addField(index, doc.keywords.join(' '), 5);

      return doc;
    }

    build() {
      const data = this.data;

      data.classes.forEach((cls) => {
        this.addDoc({
          id: cls.id,
          kind: 'class',
          title: cls.name,
          subtitle: 'Clase ' + String(cls.number).padStart(2, '0') + ' · ' + cls.id,
          context: 'Clase · ' + cls.id,
          body: [
            cls.description || '',
            cls.nameEn || '',
            (cls.keywords || []).join(' ')
          ].join(' '),
          keywords: cls.keywords || [],
          href: cls.href,
          classId: cls.id
        });

        cls.families.forEach((family) => {
          this.addDoc({
            id: family.id,
            kind: 'family',
            title: family.name,
            subtitle: 'Familia · ' + family.id,
            context: cls.id + ' · ' + cls.name,
            body: [
              family.description || '',
              family.nameEn || '',
              family.components.map(function (component) { return component.name; }).join(' '),
              (family.keywords || []).join(' ')
            ].join(' '),
            keywords: family.keywords || [],
            href: family.href,
            classId: cls.id,
            familyId: family.id
          });

          family.components.forEach((component) => {
            const elementText = component.elements.map(function (element) {
              return element.blocks.map(function (block) {
                return block.type === 'list' ? block.items.join(' ') : block.text;
              }).join(' ');
            }).join(' ');

            const managementText = (component.management || []).join(' ');
            const auditText = (component.audit || []).map(function (item) { return item.level + ' ' + item.text; }).join(' ');
            const dependencyText = (component.dependencies || []).map(function (dependency) {
              return dependency.id + ' ' + dependency.name;
            }).join(' ');

            this.addDoc({
              id: component.id,
              kind: 'component',
              title: component.name,
              subtitle: component.id + ' · Componente',
              context: family.id + ' · ' + family.name,
              body: [
                component.summary || '',
                component.nameEn || '',
                elementText,
                managementText,
                auditText,
                dependencyText,
                cls.name,
                family.name,
                (component.keywords || []).join(' ')
              ].join(' '),
              keywords: component.keywords || [],
              href: component.href,
              classId: cls.id,
              familyId: family.id,
              componentId: component.id,
              available: component.available
            });

            component.elements.forEach((element) => {
              const text = element.blocks.map(function (block) {
                return block.type === 'list' ? block.items.join(' ') : block.text;
              }).join(' ');

              this.addDoc({
                id: element.id,
                kind: 'element',
                title: element.id,
                subtitle: 'Elemento de ' + component.id + ' · ' + component.name,
                context: family.id + ' · ' + family.name,
                body: text,
                href: element.href,
                classId: cls.id,
                familyId: family.id,
                componentId: component.id,
                elementId: element.id
              });
            });
          });
        });
      });
    }

    expandPrefix(token) {
      if (token.length < 2 || /^\d+$/.test(token)) {
        return this.postings.has(token) ? [token] : [];
      }

      let low = 0;
      let high = this.vocabularyList.length;
      while (low < high) {
        const middle = (low + high) >> 1;
        if (this.vocabularyList[middle] < token) low = middle + 1;
        else high = middle;
      }

      const variants = [];
      const limit = 80;
      for (let index = low; index < this.vocabularyList.length && variants.length < limit; index += 1) {
        const candidate = this.vocabularyList[index];
        if (!candidate.startsWith(token)) break;
        variants.push(candidate);
      }

      return variants;
    }

    search(query, options) {
      const settings = options || {};
      const rawQuery = String(query == null ? '' : query).trim();
      const normalizedQuery = utils.normalizeText(rawQuery);
      const started = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();

      const emptyResult = {
        query: rawQuery,
        results: [],
        total: 0,
        facets: { all: 0, class: 0, family: 0, component: 0, element: 0 },
        took: 0
      };

      if (!rawQuery) {
        const facets = { all: 0, class: 0, family: 0, component: 0, element: 0 };

        this.docs.forEach(function (doc) {
          if (settings.classId && doc.classId !== settings.classId) return;
          facets.all += 1;
          facets[doc.kind] += 1;
        });

        return {
          query: rawQuery,
          results: [],
          total: 0,
          facets: facets,
          took: 0
        };
      }

      const rawTokens = tokenize(rawQuery);
      let queryTokens = rawTokens.filter(function (token) { return !STOPWORDS.has(token); });
      if (!queryTokens.length) queryTokens = rawTokens;
      queryTokens = Array.from(new Set(queryTokens));

      if (!queryTokens.length) return emptyResult;

      const scores = new Map();
      const matchedByDoc = new Map();
      const idQuery = isIdQuery(rawQuery) ? rawQuery.toUpperCase() : '';

      queryTokens.forEach(function (token, tokenIndex) {
        const variants = this.expandPrefix(token);
        const bestByDoc = new Map();

        variants.forEach(function (variant) {
          const bucket = this.postings.get(variant);
          if (!bucket) return;
          bucket.forEach(function (weight, docIndex) {
            const previous = bestByDoc.get(docIndex) || 0;
            if (weight > previous) bestByDoc.set(docIndex, weight);
          });
        }, this);

        bestByDoc.forEach(function (weight, docIndex) {
          scores.set(docIndex, (scores.get(docIndex) || 0) + weight);
          let matched = matchedByDoc.get(docIndex);
          if (!matched) {
            matched = new Set();
            matchedByDoc.set(docIndex, matched);
          }
          matched.add(tokenIndex);
        });
      }, this);

      this.docs.forEach(function (doc) {
        if (!idQuery) return;

        const id = doc.id.toUpperCase();
        const index = doc._index;

        if (id === idQuery) {
          scores.set(index, (scores.get(index) || 0) + 220);
          matchedByDoc.set(index, new Set(queryTokens.map(function (_, tokenIndex) { return tokenIndex; })));
        } else if (id.startsWith(idQuery + '.') || id.startsWith(idQuery + '_')) {
          scores.set(index, (scores.get(index) || 0) + 70);
        }
      });

      const result = [];
      const facets = { all: 0, class: 0, family: 0, component: 0, element: 0 };

      scores.forEach(function (baseScore, docIndex) {
        const doc = this.docs[docIndex];
        if (!doc) return;
        if (settings.classId && doc.classId !== settings.classId) return;

        let score = baseScore;
        const matched = matchedByDoc.get(docIndex) || new Set();

        if (normalizedQuery.length > 2) {
          if (doc._idNorm === normalizedQuery) score += 240;
          else if (doc._idNorm.startsWith(normalizedQuery)) score += 60;

          if (doc._titleNorm.includes(normalizedQuery)) score += 34;
          if (doc._bodyNorm.includes(normalizedQuery)) score += 8;
        }

        const coverage = queryTokens.length ? matched.size / queryTokens.length : 0;
        score *= 0.58 + (0.42 * coverage);

        if (doc.kind === 'component') score *= 1.06;
        if (doc.kind === 'element' && doc.available === false) score *= 0.96;

        facets.all += 1;
        facets[doc.kind] += 1;

        if (settings.type && settings.type !== 'all' && doc.kind !== settings.type) return;

        result.push({
          doc: doc,
          score: score,
          snippet: utils.makeSnippet(doc.body || doc.context || doc.title, rawQuery, 210),
          kindLabel: KIND_LABEL[doc.kind]
        });
      }, this);

      result.sort(function (a, b) {
        if (b.score !== a.score) return b.score - a.score;
        const kindDifference = (KIND_RANK[a.doc.kind] || 9) - (KIND_RANK[b.doc.kind] || 9);
        if (kindDifference !== 0) return kindDifference;
        return a.doc.title.localeCompare(b.doc.title, 'es');
      });

      const limit = settings.limit || 80;
      const ended = (typeof performance !== 'undefined' && performance.now) ? performance.now() : Date.now();

      return {
        query: rawQuery,
        results: result.slice(0, limit),
        total: result.length,
        facets: facets,
        took: Math.max(0, ended - started)
      };
    }

    getDoc(id) {
      return this.docById.get(String(id).toUpperCase()) || null;
    }
  }

  CC.SearchEngine = SearchEngine;
  CC.searchHelpers = { tokenize, isIdQuery };
})(window);

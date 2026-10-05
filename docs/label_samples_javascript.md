# JavaScript Label Samples

Reviewing label noise: True SZZ can erroneously label refactoring or style changes as bugs if keywords match.

### Buggy: 1 (Commit: 305feb9058f38363e25c61d69985b9393b16cc2a)
**Repo**: react
```javascript
function Test({showLateChild}) {
          return (
            <Fragment ref={outerFragmentRef}>
              <html>
                <body>
                  <Fragment ref={innerFragmentRef}>
                    <div id="child" />
                    {showLateChild && <span ref={lateChildRef} id="late" />}
                  </Fragment>
                </body>
              </html>
            </Fragment>
          );
        }
```

### Buggy: 1 (Commit: e6183e8704e98b67439268cf01dfbabb29e189f9)
**Repo**: webpack
```javascript
ast.isConstant = function isConstant(self) {
		if (isConstantNode(self)) return !isRegExpNode(self);
		return (
			isUnaryPrefixNode(self) &&
			CONSTANT_UNARY.has(self.operator) &&
			(isConstantNode(self.argument) || ast.isConstant(self.argument))
		);
	}
```

### Buggy: 1 (Commit: 520dd77a35922fb537e2dbfb3c839d047acbdd68)
**Repo**: eslint
```javascript
function normalizeMultiArgReportCall(...args) {
	// If there is one argument, it is considered to be a new-style call already.
	if (args.length === 1) {
		// Shallow clone the object to avoid surprises if reusing the descriptor
		return Object.assign({}, args[0]);
	}

	// If the second argument is a string, the arguments are interpreted as [node, message, data, fix].
	if (typeof args[1] === "string") {
		return {
			node: args[0],
			message: args[1],
			data: args[2],
			fix: args[3],
		};
	}

	// Otherwise, the arguments are interpreted as [node, loc, message, data, fix].
	return {
		node: args[0],
		loc: args[1],
		message: args[2],
		data: args[3],
		fix: args[4],
	};
}
```

### Buggy: 1 (Commit: 475893a105ac04967f702ce43561adde8d18f55b)
**Repo**: prettier
```javascript
function printCssDeclaration(path, options, print) {
  const { node, parent } = path;

  const { between: rawBetween } = node.raws;
  const trimmedBetween = rawBetween.trim();
  const isColon = trimmedBetween === ":";
  const hasSpaceAfterColon = rawBetween.endsWith(" ") && isColon;
  const isValueAllSpace =
    typeof node.value === "string" && /^ *$/.test(node.value);
  let value = typeof node.value === "string" ? node.value : print("value");

  value = hasComposesNode(node) ? removeLines(value) : value;

  if (
    !isColon &&
    lastLineHasInlineComment(trimmedBetween) &&
    !path.call(() => shouldBreakList(path), "value", "group", "group")
  ) {
    value = indent([hardline, dedent(value)]);
  }

  const parts = [
    node.raws.before.replaceAll(/[\s;]/g, ""),
    // Less variable
    (parent.type === "css-atrule" && parent.variable) ||
    insideIcssRuleNode(path)
      ? node.prop
      : maybeToLowerCase(node.prop),
  ];

  if (trimmedBetween.startsWith("//")) {
    parts.push(" ");
  }

  parts.push(trimmedBetween);

  if (!(
    node.extend ||
    isValueAllSpace ||
    (!hasSpaceAfterColon &&
      node.isNested &&
      (isAtWordPlaceholderNode(node.value.group.group) ||
        isAtWordPlaceholderNode(node.value.group.group.groups?.[0])))
  )) {
    parts.push(" ");
  }

  if (options.parser === "less" && node.extend && node.selector) {
    parts.push(
      node.selector.nodes.length > 1
        ? group([
            "extend(",
            indent([softline, print("selector")]),
            softline,
            ")",
          ])
        : ["extend(", print("selector"), ")"],
    );
  }

  parts.push(value);

  if (node.raws.important) {
    parts.push(node.raws.important.replace(/\s*!\s*important/i, " !important"));
  } else if (node.important) {
    parts.push(" !important");
  }

  if (node.raws.scssDefault) {
    parts.push(node.raws.scssDefault.replace(/\s*!default/i, " !default"));
  } else if (node.scssDefault) {
    parts.push(" !default");
  }

  if (node.raws.scssGlobal) {
    parts.push(node.raws.scssGlobal.replace(/\s*!global/i, " !global"));
  } else if (node.scssGlobal) {
    parts.push(" !global");
  }

  if (node.nodes) {
    parts.push([
      " {",
      node.nodes.length > 0
        ? indent([softline, printSequence(path, options, print)])
        : "",
      softline,
      "}",
    ]);
  } else if (!(
    isTemplatePropNode(node) &&
    !parent.raws.semicolon &&
    options.originalText[locEnd(node) - 1] !== ";"
  )) {
    parts.push(
      options.__isHTMLStyleAttribute && path.isLast ? ifBreak(";") : ";",
    );
  }

  return parts;
}
```

### Buggy: 1 (Commit: 430bd41ab24028d69aae1166762d771fc71339f1)
**Repo**: webpack
```javascript
function we(t,{instancePath:n="",parentData:o,parentDataProperty:s,rootData:i=t}={}){let a=null,l=0;if(0===l){if(!t||"object"!=typeof t||Array.isArray(t))return we.errors=[{params:{type:"object"}}],!1;{const o=l;for(const e in t)if(!r.call(q.properties,e))return we.errors=[{params:{additionalProperty:e}}],!1;if(o===l){if(void 0!==t.defaultRules){const e=l,r=l;let o=!1,s=null;const f=l;if(fe(t.defaultRules,{instancePath:n+"/defaultRules",parentData:t,parentDataProperty:"defaultRules",rootData:i})||(a=null===a?fe.errors:a.concat(fe.errors),l=a.length),f===l&&(o=!0,s=0),!o){const e={params:{passingSchemas:s}};return null===a?a=[e]:a.push(e),l++,we.errors=a,!1}l=r,null!==a&&(r?a.length=r:a=null);var p=e===l}else p=!0;if(p){if(void 0!==t.exprContextCritical){const e=l;if("boolean"!=typeof t.exprContextCritical)return we.errors=[{params:{type:"boolean"}}],!1;p=e===l}else p=!0;if(p){if(void 0!==t.exprContextRecursive){const e=l;if("boolean"!=typeof t.exprContextRecursive)return we.errors=[{params:{type:"boolean"}}],!1;p=e===l}else p=!0;if(p){if(void 0!==t.exprContextRegExp){let e=t.exprContextRegExp;const n=l,r=l;let o=!1;const s=l;if(!(e instanceof RegExp)){const e={params:{}};null===a?a=[e]:a.push(e),l++}var f=s===l;if(o=o||f,!o){const t=l;if("boolean"!=typeof e){const e={params:{type:"boolean"}};null===a?a=[e]:a.push(e),l++}f=t===l,o=o||f}if(!o){const e={params:{}};return null===a?a=[e]:a.push(e),l++,we.errors=a,!1}l=r,null!==a&&(r?a.length=r:a=null),p=n===l}else p=!0;if(p){if(void 0!==t.exprContextRequest){const e=l;if("string"!=typeof t.exprContextRequest)return we.errors=[{params:{type:"string"}}],!1;p=e===l}else p=!0;if(p){if(void 0!==t.generator){const e=l;ve(t.generator,{instancePath:n+"/generator",parentData:t,parentDataProperty:"generator",rootData:i})||(a=null===a?ve.errors:a.concat(ve.errors),l=a.length),p=e===l}else p=!0;if(p){if(void 0!==t.noParse){let n=t.noParse;const r=l,o=l;let s=!1;const i=l;if(l===i)if(Array.isArray(n))if(n.length<1){const e={params:{limit:1}};null===a?a=[e]:a.push(e),l++}else{const t=n.length;for(let r=0;r<t;r++){let t=n[r];const o=l,s=l;let i=!1;const p=l;if(!(t instanceof RegExp)){const e={params:{}};null===a?a=[e]:a.push(e),l++}var u=p===l;if(i=i||u,!i){const n=l;if(l===n)if("string"==typeof t){if(t.includes("!")||!0!==e.test(t)){const e={params:{}};null===a?a=[e]:a.push(e),l++}}else{const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}if(u=n===l,i=i||u,!i){const e=l;if(!(t instanceof Function)){const e={params:{}};null===a?a=[e]:a.push(e),l++}u=e===l,i=i||u}}if(i)l=s,null!==a&&(s?a.length=s:a=null);else{const e={params:{}};null===a?a=[e]:a.push(e),l++}if(o!==l)break}}else{const e={params:{type:"array"}};null===a?a=[e]:a.push(e),l++}var c=i===l;if(s=s||c,!s){const t=l;if(!(n instanceof RegExp)){const e={params:{}};null===a?a=[e]:a.push(e),l++}if(c=t===l,s=s||c,!s){const t=l;if(l===t)if("string"==typeof n){if(n.includes("!")||!0!==e.test(n)){const e={params:{}};null===a?a=[e]:a.push(e),l++}}else{const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}if(c=t===l,s=s||c,!s){const e=l;if(!(n instanceof Function)){const e={params:{}};null===a?a=[e]:a.push(e),l++}c=e===l,s=s||c}}}if(!s){const e={params:{}};return null===a?a=[e]:a.push(e),l++,we.errors=a,!1}l=o,null!==a&&(o?a.length=o:a=null),p=r===l}else p=!0;if(p){if(void 0!==t.parser){const e=l;Ie(t.parser,{instancePath:n+"/parser",parentData:t,parentDataProperty:"parser",rootData:i})||(a=null===a?Ie.errors:a.concat(Ie.errors),l=a.length),p=e===l}else p=!0;if(p){if(void 0!==t.rules){const e=l,r=l;let o=!1,s=null;const f=l;if(fe(t.rules,{instancePath:n+"/rules",parentData:t,parentDataProperty:"rules",rootData:i})||(a=null===a?fe.errors:a.concat(fe.errors),l=a.length),f===l&&(o=!0,s=0),!o){const e={params:{passingSchemas:s}};return null===a?a=[e]:a.push(e),l++,we.errors=a,!1}l=r,null!==a&&(r?a.length=r:a=null),p=e===l}else p=!0;if(p){if(void 0!==t.strictExportPresence){const e=l;if("boolean"!=typeof t.strictExportPresence)return we.errors=[{params:{type:"boolean"}}],!1;p=e===l}else p=!0;if(p){if(void 0!==t.strictThisContextOnImports){const e=l;if("boolean"!=typeof t.strictThisContextOnImports)return we.errors=[{params:{type:"boolean"}}],!1;p=e===l}else p=!0;if(p){if(void 0!==t.unknownContextCritical){const e=l;if("boolean"!=typeof t.unknownContextCritical)return we.errors=[{params:{type:"boolean"}}],!1;p=e===l}else p=!0;if(p){if(void 0!==t.unknownContextRecursive){const e=l;if("boolean"!=typeof t.unknownContextRecursive)return we.errors=[{params:{type:"boolean"}}],!1;p=e===l}else p=!0;if(p){if(void 0!==t.unknownContextRegExp){let e=t.unknownContextRegExp;const n=l,r=l;let o=!1;const s=l;if(!(e instanceof RegExp)){const e={params:{}};null===a?a=[e]:a.push(e),l++}var y=s===l;if(o=o||y,!o){const t=l;if("boolean"!=typeof e){const e={params:{type:"boolean"}};null===a?a=[e]:a.push(e),l++}y=t===l,o=o||y}if(!o){const e={params:{}};return null===a?a=[e]:a.push(e),l++,we.errors=a,!1}l=r,null!==a&&(r?a.length=r:a=null),p=n===l}else p=!0;if(p){if(void 0!==t.unknownContextRequest){const e=l;if("string"!=typeof t.unknownContextRequest)return we.errors=[{params:{type:"string"}}],!1;p=e===l}else p=!0;if(p){if(void 0!==t.unsafeCache){let e=t.unsafeCache;const n=l,r=l;let o=!1;const s=l;if("boolean"!=typeof e){const e={params:{type:"boolean"}};null===a?a=[e]:a.push(e),l++}var m=s===l;if(o=o||m,!o){const t=l;if(!(e instanceof Function)){const e={params:{}};null===a?a=[e]:a.push(e),l++}m=t===l,o=o||m}if(!o){const e={params:{}};return null===a?a=[e]:a.push(e),l++,we.errors=a,!1}l=r,null!==a&&(r?a.length=r:a=null),p=n===l}else p=!0;if(p){if(void 0!==t.wrappedContextCritical){const e=l;if("boolean"!=typeof t.wrappedContextCritical)return we.errors=[{params:{type:"boolean"}}],!1;p=e===l}else p=!0;if(p){if(void 0!==t.wrappedContextRecursive){const e=l;if("boolean"!=typeof t.wrappedContextRecursive)return we.errors=[{params:{type:"boolean"}}],!1;p=e===l}else p=!0;if(p)if(void 0!==t.wrappedContextRegExp){const e=l;if(!(t.wrappedContextRegExp instanceof RegExp))return we.errors=[{params:{}}],!1;p=e===l}else p=!0}}}}}}}}}}}}}}}}}}}}return we.errors=a,0===l}
```

### Buggy: 1 (Commit: a24fd0ca6cfd29329444fddf678bcdd1c08e56ae)
**Repo**: express
```javascript
function shouldNotHaveHeader(header) {
  return function (res) {
    assert.ok(!(header.toLowerCase() in res.headers), 'should not have header ' + header);
  };
}
```

### Buggy: 0 (Commit: b766f660b19096de478e5d5e5d9df9e6462be72b)
**Repo**: prettier
```javascript
function inside(code) {
      switch (code) {
        case closingCode:
          effects.consume(code);
          return mayClose;
        case codes.eof:
          return nok(code);
        default:
          if (markdownLineEnding(code)) {
            effects.exit(types.data);
            effects.enter(types.lineEnding);
            effects.consume(code);
            effects.exit(types.lineEnding);
            effects.enter(types.data);
            return inside;
          }
          effects.consume(code);
          return inside;
      }
    }
```

### Buggy: 1 (Commit: e1a8a57519d1b896c2a795d0ec0138fe24a77a33)
**Repo**: axios
```javascript
function setHeader(_value, _header, _rewrite) {
      const lHeader = normalizeHeader(_header);

      if (!lHeader) {
        return;
      }

      const key = utils.findKey(self, lHeader);

      if (
        !key ||
        self[key] === undefined ||
        _rewrite === true ||
        (_rewrite === undefined && self[key] !== false)
      ) {
        self[key || _header] = normalizeValue(_value);
      }
    }
```

### Buggy: 1 (Commit: 5a0fdd97400293ac6b39a0d01b92610528c8f4d9)
**Repo**: prettier
```javascript
function getEnclosingAssignmentChainExpressionStatement(node, ancestors) {
  let child = node;

  for (const ancestor of ancestors) {
    if (ancestor.type === "AssignmentExpression" && ancestor.right === child) {
      child = ancestor;
      continue;
    }

    return ancestor.type === "ExpressionStatement" &&
      ancestor.expression === child
      ? ancestor
      : undefined;
  }
}
```

### Buggy: 1 (Commit: d9d09b8b9041504b645f3173ca70ef173c7e1563)
**Repo**: express
```javascript
exports.wetag = function wetag(body, encoding){
  var buf = !Buffer.isBuffer(body)
    ? new Buffer(body, encoding)
    : body;

  return etag(buf, {weak: true});
}
```

### Buggy: 1 (Commit: caa4f68ee8d32474676fa29cc2086dcc1d62208b)
**Repo**: express
```javascript
res.links = function(links){
  var link = this.get('Link') || '';
  if (link) link += ', ';
  return this.set('Link', link + Object.keys(links).map(function(rel){
    return '<' + links[rel] + '>; rel="' + rel + '"';
  }).join(', '));
}
```

### Buggy: 1 (Commit: b07aa7d643ec9028e452612c3ff2c17a6cee6bb7)
**Repo**: react
```javascript
async function action(arg) {
      return arg;
    }
```

### Buggy: 1 (Commit: cec5780db4f07a61e21e139e38af20b02dd5ae3a)
**Repo**: express
```javascript
proto.param = function param(name, fn) {
  if (!fn) {
    throw new TypeError('argument fn is required');
  }

  if (typeof fn !== 'function') {
    throw new TypeError('argument fn must be a function');
  }

  var params = this.params[name];

  if (!params) {
    params = this.params[name] = [];
  }

  params.push(fn);

  return this;
}
```

### Buggy: 1 (Commit: a79c3cb5ef83a572d9319a8bef7ff17149566440)
**Repo**: webpack
```javascript
ast.isCallExpressionNode = (n) => isNode(n) && n.type === "CallExpression"
```

### Buggy: 0 (Commit: 2df1ad26a58bf51228d7600df0d62ed17a90ff71)
**Repo**: express
```javascript
app.init = function init() {
  this.cache = {};
  this.engines = {};
  this.settings = {};

  this.defaultConfiguration();
}
```

### Buggy: 0 (Commit: 30499d6af0961ec38619792013a534d1933b08a9)
**Repo**: axios
```javascript
clearAllCookies = () => {
  const expiry = new Date(Date.now() - 86400000).toUTCString();

  for (const cookie of document.cookie.split(';')) {
    const name = cookie.split('=')[0].trim();

    if (!name) {
      continue;
    }

    // Clear both default-path and root-path cookies for the same key.
    document.cookie = `${name}=; expires=${expiry}`;
    document.cookie = `${name}=; expires=${expiry}; path=/`;
  }
}
```

### Buggy: 1 (Commit: 1b7584664da1e1e504ca30fd2630bb8f8ab2347a)
**Repo**: vue
```javascript
function isObject(obj) {
    return obj !== null && typeof obj === 'object'
  }
```

### Buggy: 1 (Commit: 1b7584664da1e1e504ca30fd2630bb8f8ab2347a)
**Repo**: vue
```javascript
function isSelectWithModel(node) {
  return (
    node.type === 1 &&
    node.tag === 'select' &&
    node.directives != null &&
    node.directives.some(function (d) {
      return d.name === 'model'
    })
  )
}
```

### Buggy: 1 (Commit: 15f7cd693e102c568df501eeeb9684f507e0ec0b)
**Repo**: react
```javascript
function clientRenderBoundary(
  suspenseBoundaryID,
  errorDigest,
  errorMsg,
  errorStack,
  errorComponentStack,
) {
  // Find the fallback's first element.
  const suspenseIdNode = document.getElementById(suspenseBoundaryID);
  if (!suspenseIdNode) {
    // The user must have already navigated away from this tree.
    // E.g. because the parent was hydrated.
    return;
  }
  // Find the boundary around the fallback. This is always the previous node.
  const suspenseNode = suspenseIdNode.previousSibling;
  // Tag it to be client rendered.
  suspenseNode.data = SUSPENSE_FALLBACK_START_DATA;
  // assign error metadata to first sibling
  const dataset = suspenseIdNode.dataset;
  if (errorDigest) dataset['dgst'] = errorDigest;
  if (errorMsg) dataset['msg'] = errorMsg;
  if (errorStack) dataset['stck'] = errorStack;
  if (errorComponentStack) dataset['cstck'] = errorComponentStack;
  // Tell React to retry it if the parent already hydrated.
  if (suspenseNode['_reactRetry']) {
    suspenseNode['_reactRetry']();
  }
}
```

### Buggy: 1 (Commit: 430bd41ab24028d69aae1166762d771fc71339f1)
**Repo**: webpack
```javascript
function pe(e,{instancePath:t="",parentData:n,parentDataProperty:o,rootData:s=e}={}){let i=null,a=0;if(0===a){if(!e||"object"!=typeof e||Array.isArray(e))return pe.errors=[{params:{type:"object"}}],!1;{const n=a;for(const t in e)if(!r.call(B.properties,t))return pe.errors=[{params:{additionalProperty:t}}],!1;if(n===a){if(void 0!==e.assert){let n=e.assert;const r=a;if(a===r){if(!n||"object"!=typeof n||Array.isArray(n))return pe.errors=[{params:{type:"object"}}],!1;for(const e in n){const r=a;if(K(n[e],{instancePath:t+"/assert/"+e.replace(/~/g,"~0").replace(/\//g,"~1"),parentData:n,parentDataProperty:e,rootData:s})||(i=null===i?K.errors:i.concat(K.errors),a=i.length),r!==a)break}}var l=r===a}else l=!0;if(l){if(void 0!==e.compiler){const n=a,r=a;let o=!1,p=null;const f=a;if(K(e.compiler,{instancePath:t+"/compiler",parentData:e,parentDataProperty:"compiler",rootData:s})||(i=null===i?K.errors:i.concat(K.errors),a=i.length),f===a&&(o=!0,p=0),!o){const e={params:{passingSchemas:p}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}a=r,null!==i&&(r?i.length=r:i=null),l=n===a}else l=!0;if(l){if(void 0!==e.dependency){const n=a,r=a;let o=!1,p=null;const f=a;if(K(e.dependency,{instancePath:t+"/dependency",parentData:e,parentDataProperty:"dependency",rootData:s})||(i=null===i?K.errors:i.concat(K.errors),a=i.length),f===a&&(o=!0,p=0),!o){const e={params:{passingSchemas:p}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}a=r,null!==i&&(r?i.length=r:i=null),l=n===a}else l=!0;if(l){if(void 0!==e.descriptionData){let n=e.descriptionData;const r=a;if(a===r){if(!n||"object"!=typeof n||Array.isArray(n))return pe.errors=[{params:{type:"object"}}],!1;for(const e in n){const r=a;if(K(n[e],{instancePath:t+"/descriptionData/"+e.replace(/~/g,"~0").replace(/\//g,"~1"),parentData:n,parentDataProperty:e,rootData:s})||(i=null===i?K.errors:i.concat(K.errors),a=i.length),r!==a)break}}l=r===a}else l=!0;if(l){if(void 0!==e.descriptionRelativePath){const n=a,r=a;let o=!1,p=null;const f=a;if(K(e.descriptionRelativePath,{instancePath:t+"/descriptionRelativePath",parentData:e,parentDataProperty:"descriptionRelativePath",rootData:s})||(i=null===i?K.errors:i.concat(K.errors),a=i.length),f===a&&(o=!0,p=0),!o){const e={params:{passingSchemas:p}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}a=r,null!==i&&(r?i.length=r:i=null),l=n===a}else l=!0;if(l){if(void 0!==e.enforce){let t=e.enforce;const n=a;if("pre"!==t&&"post"!==t)return pe.errors=[{params:{}}],!1;l=n===a}else l=!0;if(l){if(void 0!==e.exclude){const n=a,r=a;let o=!1,p=null;const f=a;if(ne(e.exclude,{instancePath:t+"/exclude",parentData:e,parentDataProperty:"exclude",rootData:s})||(i=null===i?ne.errors:i.concat(ne.errors),a=i.length),f===a&&(o=!0,p=0),!o){const e={params:{passingSchemas:p}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}a=r,null!==i&&(r?i.length=r:i=null),l=n===a}else l=!0;if(l){if(void 0!==e.extractSourceMap){const t=a;if("boolean"!=typeof e.extractSourceMap)return pe.errors=[{params:{type:"boolean"}}],!1;l=t===a}else l=!0;if(l){if(void 0!==e.generator){let t=e.generator;const n=a;if(!t||"object"!=typeof t||Array.isArray(t))return pe.errors=[{params:{type:"object"}}],!1;l=n===a}else l=!0;if(l){if(void 0!==e.glob){let n=e.glob;const r=a,o=a;let f=!1;const u=a;if(a==a)if("string"==typeof n){if(n.length<1){const e={params:{}};null===i?i=[e]:i.push(e),a++}}else{const e={params:{type:"string"}};null===i?i=[e]:i.push(e),a++}var p=u===a;if(f=f||p,!f){const r=a;_(n,{instancePath:t+"/glob",parentData:e,parentDataProperty:"glob",rootData:s})||(i=null===i?_.errors:i.concat(_.errors),a=i.length),p=r===a,f=f||p}if(!f){const e={params:{}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}a=o,null!==i&&(o?i.length=o:i=null),l=r===a}else l=!0;if(l){if(void 0!==e.include){const n=a,r=a;let o=!1,p=null;const f=a;if(ne(e.include,{instancePath:t+"/include",parentData:e,parentDataProperty:"include",rootData:s})||(i=null===i?ne.errors:i.concat(ne.errors),a=i.length),f===a&&(o=!0,p=0),!o){const e={params:{passingSchemas:p}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}a=r,null!==i&&(r?i.length=r:i=null),l=n===a}else l=!0;if(l){if(void 0!==e.issuer){const n=a,r=a;let o=!1,p=null;const f=a;if(ne(e.issuer,{instancePath:t+"/issuer",parentData:e,parentDataProperty:"issuer",rootData:s})||(i=null===i?ne.errors:i.concat(ne.errors),a=i.length),f===a&&(o=!0,p=0),!o){const e={params:{passingSchemas:p}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}a=r,null!==i&&(r?i.length=r:i=null),l=n===a}else l=!0;if(l){if(void 0!==e.issuerLayer){const n=a,r=a;let o=!1,p=null;const f=a;if(K(e.issuerLayer,{instancePath:t+"/issuerLayer",parentData:e,parentDataProperty:"issuerLayer",rootData:s})||(i=null===i?K.errors:i.concat(K.errors),a=i.length),f===a&&(o=!0,p=0),!o){const e={params:{passingSchemas:p}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}a=r,null!==i&&(r?i.length=r:i=null),l=n===a}else l=!0;if(l){if(void 0!==e.layer){const t=a;if("string"!=typeof e.layer)return pe.errors=[{params:{type:"string"}}],!1;l=t===a}else l=!0;if(l){if(void 0!==e.loader){let t=e.loader;const n=a,r=a;let o=!1,s=null;const p=a;if(a==a)if("string"==typeof t){if(t.length<1){const e={params:{}};null===i?i=[e]:i.push(e),a++}}else{const e={params:{type:"string"}};null===i?i=[e]:i.push(e),a++}if(p===a&&(o=!0,s=0),!o){const e={params:{passingSchemas:s}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}a=r,null!==i&&(r?i.length=r:i=null),l=n===a}else l=!0;if(l){if(void 0!==e.mimetype){const n=a,r=a;let o=!1,p=null;const f=a;if(K(e.mimetype,{instancePath:t+"/mimetype",parentData:e,parentDataProperty:"mimetype",rootData:s})||(i=null===i?K.errors:i.concat(K.errors),a=i.length),f===a&&(o=!0,p=0),!o){const e={params:{passingSchemas:p}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}a=r,null!==i&&(r?i.length=r:i=null),l=n===a}else l=!0;if(l){if(void 0!==e.oneOf){let n=e.oneOf;const r=a;if(a===r){if(!Array.isArray(n))return pe.errors=[{params:{type:"array"}}],!1;{const e=n.length;for(let r=0;r<e;r++){let e=n[r];const o=a,l=a;let p=!1;const u=a;if(!1!==e&&0!==e&&""!==e&&null!=e){const e={params:{}};null===i?i=[e]:i.push(e),a++}var f=u===a;if(p=p||f,!p){const o=a;le.validate(e,{instancePath:t+"/oneOf/"+r,parentData:n,parentDataProperty:r,rootData:s})||(i=null===i?le.validate.errors:i.concat(le.validate.errors),a=i.length),f=o===a,p=p||f}if(!p){const e={params:{}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}if(a=l,null!==i&&(l?i.length=l:i=null),o!==a)break}}}l=r===a}else l=!0;if(l){if(void 0!==e.options){let t=e.options;const n=a,r=a;let o=!1,s=null;const p=a,f=a;let c=!1;const y=a;if("string"!=typeof t){const e={params:{type:"string"}};null===i?i=[e]:i.push(e),a++}var u=y===a;if(c=c||u,!c){const e=a;if(!t||"object"!=typeof t||Array.isArray(t)){const e={params:{type:"object"}};null===i?i=[e]:i.push(e),a++}u=e===a,c=c||u}if(c)a=f,null!==i&&(f?i.length=f:i=null);else{const e={params:{}};null===i?i=[e]:i.push(e),a++}if(p===a&&(o=!0,s=0),!o){const e={params:{passingSchemas:s}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}a=r,null!==i&&(r?i.length=r:i=null),l=n===a}else l=!0;if(l){if(void 0!==e.parser){let t=e.parser;const n=a;if(a===n&&(!t||"object"!=typeof t||Array.isArray(t)))return pe.errors=[{params:{type:"object"}}],!1;l=n===a}else l=!0;if(l){if(void 0!==e.phase){const n=a,r=a;let o=!1,p=null;const f=a;if(K(e.phase,{instancePath:t+"/phase",parentData:e,parentDataProperty:"phase",rootData:s})||(i=null===i?K.errors:i.concat(K.errors),a=i.length),f===a&&(o=!0,p=0),!o){const e={params:{passingSchemas:p}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}a=r,null!==i&&(r?i.length=r:i=null),l=n===a}else l=!0;if(l){if(void 0!==e.realResource){const n=a,r=a;let o=!1,p=null;const f=a;if(ne(e.realResource,{instancePath:t+"/realResource",parentData:e,parentDataProperty:"realResource",rootData:s})||(i=null===i?ne.errors:i.concat(ne.errors),a=i.length),f===a&&(o=!0,p=0),!o){const e={params:{passingSchemas:p}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}a=r,null!==i&&(r?i.length=r:i=null),l=n===a}else l=!0;if(l){if(void 0!==e.resolve){let n=e.resolve;const r=a;if(!n||"object"!=typeof n||Array.isArray(n))return pe.errors=[{params:{type:"object"}}],!1;const o=a;let p=!1,f=null;const u=a;if(se(n,{instancePath:t+"/resolve",parentData:e,parentDataProperty:"resolve",rootData:s})||(i=null===i?se.errors:i.concat(se.errors),a=i.length),u===a&&(p=!0,f=0),!p){const e={params:{passingSchemas:f}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}a=o,null!==i&&(o?i.length=o:i=null),l=r===a}else l=!0;if(l){if(void 0!==e.resource){const n=a,r=a;let o=!1,p=null;const f=a;if(ne(e.resource,{instancePath:t+"/resource",parentData:e,parentDataProperty:"resource",rootData:s})||(i=null===i?ne.errors:i.concat(ne.errors),a=i.length),f===a&&(o=!0,p=0),!o){const e={params:{passingSchemas:p}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}a=r,null!==i&&(r?i.length=r:i=null),l=n===a}else l=!0;if(l){if(void 0!==e.resourceFragment){const n=a,r=a;let o=!1,p=null;const f=a;if(K(e.resourceFragment,{instancePath:t+"/resourceFragment",parentData:e,parentDataProperty:"resourceFragment",rootData:s})||(i=null===i?K.errors:i.concat(K.errors),a=i.length),f===a&&(o=!0,p=0),!o){const e={params:{passingSchemas:p}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}a=r,null!==i&&(r?i.length=r:i=null),l=n===a}else l=!0;if(l){if(void 0!==e.resourceQuery){const n=a,r=a;let o=!1,p=null;const f=a;if(K(e.resourceQuery,{instancePath:t+"/resourceQuery",parentData:e,parentDataProperty:"resourceQuery",rootData:s})||(i=null===i?K.errors:i.concat(K.errors),a=i.length),f===a&&(o=!0,p=0),!o){const e={params:{passingSchemas:p}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}a=r,null!==i&&(r?i.length=r:i=null),l=n===a}else l=!0;if(l){if(void 0!==e.rules){let n=e.rules;const r=a;if(a===r){if(!Array.isArray(n))return pe.errors=[{params:{type:"array"}}],!1;{const e=n.length;for(let r=0;r<e;r++){let e=n[r];const o=a,l=a;let p=!1;const f=a;if(!1!==e&&0!==e&&""!==e&&null!=e){const e={params:{}};null===i?i=[e]:i.push(e),a++}var c=f===a;if(p=p||c,!p){const o=a;le.validate(e,{instancePath:t+"/rules/"+r,parentData:n,parentDataProperty:r,rootData:s})||(i=null===i?le.validate.errors:i.concat(le.validate.errors),a=i.length),c=o===a,p=p||c}if(!p){const e={params:{}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}if(a=l,null!==i&&(l?i.length=l:i=null),o!==a)break}}}l=r===a}else l=!0;if(l){if(void 0!==e.scheme){const n=a,r=a;let o=!1,p=null;const f=a;if(K(e.scheme,{instancePath:t+"/scheme",parentData:e,parentDataProperty:"scheme",rootData:s})||(i=null===i?K.errors:i.concat(K.errors),a=i.length),f===a&&(o=!0,p=0),!o){const e={params:{passingSchemas:p}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}a=r,null!==i&&(r?i.length=r:i=null),l=n===a}else l=!0;if(l){if(void 0!==e.sideEffects){const t=a;if("boolean"!=typeof e.sideEffects)return pe.errors=[{params:{type:"boolean"}}],!1;l=t===a}else l=!0;if(l){if(void 0!==e.test){const n=a,r=a;let o=!1,p=null;const f=a;if(ne(e.test,{instancePath:t+"/test",parentData:e,parentDataProperty:"test",rootData:s})||(i=null===i?ne.errors:i.concat(ne.errors),a=i.length),f===a&&(o=!0,p=0),!o){const e={params:{passingSchemas:p}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}a=r,null!==i&&(r?i.length=r:i=null),l=n===a}else l=!0;if(l){if(void 0!==e.type){const t=a;if("string"!=typeof e.type)return pe.errors=[{params:{type:"string"}}],!1;l=t===a}else l=!0;if(l){if(void 0!==e.use){const n=a,r=a;let o=!1,p=null;const f=a;if(ae(e.use,{instancePath:t+"/use",parentData:e,parentDataProperty:"use",rootData:s})||(i=null===i?ae.errors:i.concat(ae.errors),a=i.length),f===a&&(o=!0,p=0),!o){const e={params:{passingSchemas:p}};return null===i?i=[e]:i.push(e),a++,pe.errors=i,!1}a=r,null!==i&&(r?i.length=r:i=null),l=n===a}else l=!0;if(l)if(void 0!==e.with){let n=e.with;const r=a;if(a===r){if(!n||"object"!=typeof n||Array.isArray(n))return pe.errors=[{params:{type:"object"}}],!1;for(const e in n){const r=a;if(K(n[e],{instancePath:t+"/with/"+e.replace(/~/g,"~0").replace(/\//g,"~1"),parentData:n,parentDataProperty:e,rootData:s})||(i=null===i?K.errors:i.concat(K.errors),a=i.length),r!==a)break}}l=r===a}else l=!0}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}return pe.errors=i,0===a}
```

### Buggy: 1 (Commit: 1b7ae3a142cd9f798ad9a89ed21ae058cfebe531)
**Repo**: react
```javascript
function processExperimental(buildDir, version) {
  if (fs.existsSync(buildDir + '/node_modules')) {
    const defaultVersionIfNotFound =
      '0.0.0' + '-experimental-' + sha + '-' + dateString;
    const versionsMap = new Map();
    for (const moduleName in stablePackages) {
      versionsMap.set(moduleName, defaultVersionIfNotFound);
    }
    for (const moduleName of experimentalPackages) {
      versionsMap.set(moduleName, defaultVersionIfNotFound);
    }
    updatePackageVersions(
      buildDir + '/node_modules',
      versionsMap,
      defaultVersionIfNotFound,
      true
    );
    fs.renameSync(buildDir + '/node_modules', buildDir + '/oss-experimental');
    updatePlaceholderReactVersionInCompiledArtifacts(
      buildDir + '/oss-experimental',
      // TODO: The npm version for experimental releases does not include the
      // React version, but the runtime version does so that DevTools can do
      // feature detection. Decide what to do about this later.
      ReactVersion + '-experimental-' + sha + '-' + dateString
    );
  }

  if (fs.existsSync(buildDir + '/facebook-www')) {
    for (const fileName of fs.readdirSync(buildDir + '/facebook-www')) {
      const filePath = buildDir + '/facebook-www/' + fileName;
      const stats = fs.statSync(filePath);
      if (!stats.isDirectory()) {
        fs.renameSync(filePath, filePath.replace('.js', '.modern.js'));
      }
    }
    const versionString =
      ReactVersion + '-www-modern-' + sha + '-' + dateString;
    updatePlaceholderReactVersionInCompiledArtifacts(
      buildDir + '/facebook-www',
      versionString
    );

    // Also save a file with the version number
    fs.writeFileSync(buildDir + '/facebook-www/VERSION_MODERN', versionString);
  }

  const rnVersionString = ReactVersion + '-native-fb-' + sha + '-' + dateString;
  if (fs.existsSync(buildDir + '/facebook-react-native')) {
    updatePlaceholderReactVersionInCompiledArtifacts(
      buildDir + '/facebook-react-native',
      rnVersionString
    );

    // Also save a file with the version number
    fs.writeFileSync(
      buildDir + '/facebook-react-native/VERSION_NATIVE_FB',
      rnVersionString
    );
  }

  if (fs.existsSync(buildDir + '/react-native')) {
    updatePlaceholderReactVersionInCompiledArtifacts(
      buildDir + '/react-native',
      rnVersionString,
      filename => filename.endsWith('.fb.js')
    );

    updatePlaceholderReactVersionInCompiledArtifacts(
      buildDir + '/react-native',
      ReactVersion,
      filename => !filename.endsWith('.fb.js') && filename.endsWith('.js')
    );
  }

  if (fs.existsSync(buildDir + '/sizes')) {
    fs.renameSync(buildDir + '/sizes', buildDir + '/sizes-experimental');
  }

  // Delete all other artifacts that weren't handled above. We assume they are
  // duplicates of the corresponding artifacts in the stable channel. Ideally,
  // the underlying build script should not have produced these files in the
  // first place.
  for (const pathName of fs.readdirSync(buildDir)) {
    if (
      pathName !== 'oss-experimental' &&
      pathName !== 'facebook-www' &&
      pathName !== 'sizes-experimental'
    ) {
      spawnSync('rm', ['-rm', buildDir + '/' + pathName]);
    }
  }
}
```

### Buggy: 1 (Commit: a79c3cb5ef83a572d9319a8bef7ff17149566440)
**Repo**: webpack
```javascript
ast.isDirectiveNode = (n) =>
		isNode(n) && n.type === "ExpressionStatement" && n.directive !== undefined
```

### Buggy: 1 (Commit: 4918457aad892a32b2b0cd585c40d22870d48c4a)
**Repo**: axios
```javascript
static from(error, code, config, request, response, customProps) {
    const axiosError = new AxiosError(error.message, code || error.code, config, request, response);
    axiosError.cause = error;
    axiosError.name = error.name;

    // Preserve status from the original error if not already set from response
    if (error.status != null && axiosError.status == null) {
      axiosError.status = error.status;
    }

    customProps && Object.assign(axiosError, customProps);
    return axiosError;
  }
```

### Buggy: 1 (Commit: 518eb6a18f851e20e49b58eb4e39c80ebc843eac)
**Repo**: prettier
```javascript
function printTitle(title, options, printSpace = true) {
  if (!title) {
    return "";
  }
  if (printSpace) {
    return " " + printTitle(title, options, false);
  }

  // title is escaped before `remark-parse` v10
  if (options.parser === "mdx") {
    title = title.replaceAll(/\\(?=["')])/g, "");
  }

  if (
    title.includes('"') &&
    title.includes("'") &&
    !title.includes("(") &&
    !title.includes(")")
  ) {
    title = title.replaceAll("\\", "\\\\");
    return `(${title})`; // avoid escaped quotes
  }
  const quote = getPreferredQuote(title, options.singleQuote);
  title = title.replaceAll("\\", "\\\\");
  title = title.replaceAll(quote, `\\${quote}`);
  return `${quote}${title}${quote}`;
}
```

### Buggy: 1 (Commit: 430bd41ab24028d69aae1166762d771fc71339f1)
**Repo**: webpack
```javascript
function F(e,{instancePath:t="",parentData:n,parentDataProperty:r,rootData:o=e}={}){let s=null,i=0;if(0===i){if(!e||"object"!=typeof e||Array.isArray(e))return F.errors=[{params:{type:"object"}}],!1;{const t=i;for(const t in e)if("backend"!==t&&"entries"!==t&&"imports"!==t&&"test"!==t)return F.errors=[{params:{additionalProperty:t}}],!1;if(t===i){if(void 0!==e.backend){let t=e.backend;const n=i,r=i;let o=!1;const y=i;if(!(t instanceof Function)){const e={params:{}};null===s?s=[e]:s.push(e),i++}var a=y===i;if(o=o||a,!o){const e=i;if(i==i)if(t&&"object"==typeof t&&!Array.isArray(t)){const e=i;for(const e in t)if("client"!==e&&"listen"!==e&&"protocol"!==e&&"server"!==e){const t={params:{additionalProperty:e}};null===s?s=[t]:s.push(t),i++;break}if(e===i){if(void 0!==t.client){const e=i;if("string"!=typeof t.client){const e={params:{type:"string"}};null===s?s=[e]:s.push(e),i++}var l=e===i}else l=!0;if(l){if(void 0!==t.listen){let e=t.listen;const n=i,r=i;let o=!1;const a=i;if("number"!=typeof e){const e={params:{type:"number"}};null===s?s=[e]:s.push(e),i++}var p=a===i;if(o=o||p,!o){const t=i;if(i===t)if(e&&"object"==typeof e&&!Array.isArray(e)){if(void 0!==e.host){const t=i;if("string"!=typeof e.host){const e={params:{type:"string"}};null===s?s=[e]:s.push(e),i++}var f=t===i}else f=!0;if(f)if(void 0!==e.port){const t=i;if("number"!=typeof e.port){const e={params:{type:"number"}};null===s?s=[e]:s.push(e),i++}f=t===i}else f=!0}else{const e={params:{type:"object"}};null===s?s=[e]:s.push(e),i++}if(p=t===i,o=o||p,!o){const t=i;if(!(e instanceof Function)){const e={params:{}};null===s?s=[e]:s.push(e),i++}p=t===i,o=o||p}}if(o)i=r,null!==s&&(r?s.length=r:s=null);else{const e={params:{}};null===s?s=[e]:s.push(e),i++}l=n===i}else l=!0;if(l){if(void 0!==t.protocol){let e=t.protocol;const n=i;if("http"!==e&&"https"!==e){const e={params:{}};null===s?s=[e]:s.push(e),i++}l=n===i}else l=!0;if(l)if(void 0!==t.server){let e=t.server;const n=i,r=i;let o=!1;const a=i;if(i===a)if(e&&"object"==typeof e&&!Array.isArray(e));else{const e={params:{type:"object"}};null===s?s=[e]:s.push(e),i++}var u=a===i;if(o=o||u,!o){const t=i;if(!(e instanceof Function)){const e={params:{}};null===s?s=[e]:s.push(e),i++}u=t===i,o=o||u}if(o)i=r,null!==s&&(r?s.length=r:s=null);else{const e={params:{}};null===s?s=[e]:s.push(e),i++}l=n===i}else l=!0}}}}else{const e={params:{type:"object"}};null===s?s=[e]:s.push(e),i++}a=e===i,o=o||a}if(!o){const e={params:{}};return null===s?s=[e]:s.push(e),i++,F.errors=s,!1}i=r,null!==s&&(r?s.length=r:s=null);var c=n===i}else c=!0;if(c){if(void 0!==e.entries){const t=i;if("boolean"!=typeof e.entries)return F.errors=[{params:{type:"boolean"}}],!1;c=t===i}else c=!0;if(c){if(void 0!==e.imports){const t=i;if("boolean"!=typeof e.imports)return F.errors=[{params:{type:"boolean"}}],!1;c=t===i}else c=!0;if(c)if(void 0!==e.test){let t=e.test;const n=i,r=i;let o=!1;const a=i;if(!(t instanceof RegExp)){const e={params:{}};null===s?s=[e]:s.push(e),i++}var y=a===i;if(o=o||y,!o){const e=i;if("string"!=typeof t){const e={params:{type:"string"}};null===s?s=[e]:s.push(e),i++}if(y=e===i,o=o||y,!o){const e=i;if(!(t instanceof Function)){const e={params:{}};null===s?s=[e]:s.push(e),i++}y=e===i,o=o||y}}if(!o){const e={params:{}};return null===s?s=[e]:s.push(e),i++,F.errors=s,!1}i=r,null!==s&&(r?s.length=r:s=null),c=n===i}else c=!0}}}}}return F.errors=s,0===i}
```

### Buggy: 1 (Commit: 34adfd90efc9c145488399e1cf7fa96de67080fa)
**Repo**: axios
```javascript
function normalizeConfigURL(config) {
  if (isURL(config.url)) {
    config.url = normalizeURL(config.url);
  }
}
```

### Buggy: 0 (Commit: 9f4a364ab0ade048dfce1f37792b1d461d866e55)
**Repo**: eslint
```javascript
function reportIfUnreachable(node) {
			let nextNode = null;

			if (
				node &&
				(node.type === "PropertyDefinition" ||
					!isAnySegmentReachable(currentCodePathSegments))
			) {
				// Store this statement to distinguish consecutive statements.
				if (range.isEmpty) {
					range.reset(node);
					return;
				}

				// Skip if this statement is inside of the current range.
				if (range.contains(node)) {
					return;
				}

				// Merge if this statement is consecutive to the current range.
				if (range.isConsecutive(node)) {
					range.merge(node);
					return;
				}

				nextNode = node;
			}

			/*
			 * Report the current range since this statement is reachable or is
			 * not consecutive to the current range.
			 */
			if (!range.isEmpty) {
				context.report({
					messageId: "unreachableCode",
					loc: range.location,
					node: range.startNode,
				});
			}

			// Update the current range.
			range.reset(nextNode);
		}
```

### Buggy: 1 (Commit: 2dc7da790d6388b95b83198ca9b588b2ad5f5c0b)
**Repo**: react
```javascript
function withEnableLegacyFBSupport(enableLegacyFBSupport) {
    describe(
      'enableLegacyFBSupport ' +
        (enableLegacyFBSupport ? 'enabled' : 'disabled'),
      () => {
        beforeAll(() => {
          // These tests are run twice, once with legacyFBSupport enabled and once disabled.
          // The document needs to be cleaned up a bit before the second pass otherwise it is
          // operating in a non pristine environment
          document.removeChild(document.documentElement);
          document.appendChild(document.createElement('html'));
          document.documentElement.appendChild(document.createElement('head'));
          document.documentElement.appendChild(document.createElement('body'));
        });

        beforeEach(() => {
          jest.resetModules();
          ReactFeatureFlags = require('shared/ReactFeatureFlags');
          ReactFeatureFlags.enableLegacyFBSupport = enableLegacyFBSupport;

          React = require('react');
          ReactDOM = require('react-dom');
          ReactDOMClient = require('react-dom/client');
          Scheduler = require('scheduler');
          ReactDOMServer = require('react-dom/server');

          const InternalTestUtils = require('internal-test-utils');
          waitForAll = InternalTestUtils.waitForAll;
          waitFor = InternalTestUtils.waitFor;
          act = InternalTestUtils.act;

          container = document.createElement('div');
          document.body.appendChild(container);
          startNativeEventListenerClearDown();
        });

        afterEach(() => {
          document.body.removeChild(container);
          container = null;
          endNativeEventListenerClearDown();
        });

        it('does not pool events', async () => {
          const buttonRef = React.createRef();
          const log = [];
          const onClick = jest.fn(e => log.push(e));

          function Test() {
            return <button ref={buttonRef} onClick={onClick} />;
          }

          const root = ReactDOMClient.createRoot(container);
          await act(() => {
            root.render(<Test />);
          });

          const buttonElement = buttonRef.current;
          dispatchClickEvent(buttonElement);
          expect(onClick).toHaveBeenCalledTimes(1);
          dispatchClickEvent(buttonElement);
          expect(onClick).toHaveBeenCalledTimes(2);
          expect(log[0]).not.toBe(log[1]);
          expect(log[0].type).toBe('click');
          expect(log[1].type).toBe('click');
        });

        it('handle propagation of click events', async () => {
          const buttonRef = React.createRef();
          const divRef = React.createRef();
          const log = [];
          const onClick = jest.fn(e => log.push(['bubble', e.currentTarget]));
          const onClickCapture = jest.fn(e =>
            log.push(['capture', e.currentTarget]),
          );

          function Test() {
            return (
              <button
                ref={buttonRef}
                onClick={onClick}
                onClickCapture={onClickCapture}>
                <div
                  ref={divRef}
                  onClick={onClick}
                  onClickCapture={onClickCapture}>
                  Click me!
                </div>
              </button>
            );
          }

          const root = ReactDOMClient.createRoot(container);
          await act(() => {
            root.render(<Test />);
          });

          const buttonElement = buttonRef.current;
          dispatchClickEvent(buttonElement);

          expect(onClick).toHaveBeenCalledTimes(1);
          expect(onClickCapture).toHaveBeenCalledTimes(1);
          expect(log[0]).toEqual(['capture', buttonElement]);
          expect(log[1]).toEqual(['bubble', buttonElement]);

          const divElement = divRef.current;
          dispatchClickEvent(divElement);
          expect(onClick).toHaveBeenCalledTimes(3);
          expect(onClickCapture).toHaveBeenCalledTimes(3);
          expect(log[2]).toEqual(['capture', buttonElement]);
          expect(log[3]).toEqual(['capture', divElement]);
          expect(log[4]).toEqual(['bubble', divElement]);
          expect(log[5]).toEqual(['bubble', buttonElement]);
        });

        it('handle propagation of click events combined with sync clicks', async () => {
          const buttonRef = React.createRef();
          let clicks = 0;

          function Test() {
            const inputRef = React.useRef(null);
            return (
              <div>
                <button
                  ref={buttonRef}
                  onClick={() => {
                    // Sync click
                    inputRef.current.click();
                  }}
                />
                <input
                  ref={inputRef}
                  onClick={() => {
                    clicks++;
                  }}
                />
              </div>
            );
          }

          const root = ReactDOMClient.createRoot(container);
          await act(() => {
            root.render(<Test />);
          });

          const buttonElement = buttonRef.current;
          dispatchClickEvent(buttonElement);

          expect(clicks).toBe(1);
        });

        it('handle propagation of click events between roots', async () => {
          const buttonRef = React.createRef();
          const divRef = React.createRef();
          const childRef = React.createRef();
          const log = [];
          const onClick = jest.fn(e => log.push(['bubble', e.currentTarget]));
          const onClickCapture = jest.fn(e =>
            log.push(['capture', e.currentTarget]),
          );

          function Child() {
            return (
              <div
                ref={divRef}
                onClick={onClick}
                onClickCapture={onClickCapture}>
                Click me!
              </div>
            );
          }

          function Parent() {
            return (
              <button
                ref={buttonRef}
                onClick={onClick}
                onClickCapture={onClickCapture}>
                <div ref={childRef} />
              </button>
            );
          }

          const root = ReactDOMClient.createRoot(container);
          await act(() => {
            root.render(<Parent />);
          });
          const childRoot = ReactDOMClient.createRoot(childRef.current);
          await act(() => {
            childRoot.render(<Child />);
          });

          const buttonElement = buttonRef.current;
          dispatchClickEvent(buttonElement);
          expect(onClick).toHaveBeenCalledTimes(1);
          expect(onClickCapture).toHaveBeenCalledTimes(1);
          expect(log[0]).toEqual(['capture', buttonElement]);
          expect(log[1]).toEqual(['bubble', buttonElement]);

          const divElement = divRef.current;
          dispatchClickEvent(divElement);
          expect(onClick).toHaveBeenCalledTimes(3);
          expect(onClickCapture).toHaveBeenCalledTimes(3);
          expect(log[2]).toEqual(['capture', buttonElement]);
          expect(log[3]).toEqual(['capture', divElement]);
          expect(log[4]).toEqual(['bubble', divElement]);
          expect(log[5]).toEqual(['bubble', buttonElement]);
        });

        it('handle propagation of click events between disjointed roots', async () => {
          const buttonRef = React.createRef();
          const divRef = React.createRef();
          const log = [];
          const onClick = jest.fn(e => log.push(['bubble', e.currentTarget]));
          const onClickCapture = jest.fn(e =>
            log.push(['capture', e.currentTarget]),
          );

          function Child() {
            return (
              <div
                ref={divRef}
                onClick={onClick}
                onClickCapture={onClickCapture}>
                Click me!
              </div>
            );
          }

          function Parent() {
            return (
              <button
                ref={buttonRef}
                onClick={onClick}
                onClickCapture={onClickCapture}
              />
            );
          }

          const disjointedNode = document.createElement('div');
          const root = ReactDOMClient.createRoot(container);
          await act(() => {
            root.render(<Parent />);
          });

          buttonRef.current.appendChild(disjointedNode);
          const disjointedNodeRoot = ReactDOMClient.createRoot(disjointedNode);
          await act(() => {
            disjointedNodeRoot.render(<Child />);
          });

          const buttonElement = buttonRef.current;
          dispatchClickEvent(buttonElement);
          expect(onClick).toHaveBeenCalledTimes(1);
          expect(onClickCapture).toHaveBeenCalledTimes(1);
          expect(log[0]).toEqual(['capture', buttonElement]);
          expect(log[1]).toEqual(['bubble', buttonElement]);

          const divElement = divRef.current;
          dispatchClickEvent(divElement);
          expect(onClick).toHaveBeenCalledTimes(3);
          expect(onClickCapture).toHaveBeenCalledTimes(3);
          expect(log[2]).toEqual(['capture', buttonElement]);
          expect(log[3]).toEqual(['capture', divElement]);
          expect(log[4]).toEqual(['bubble', divElement]);
          expect(log[5]).toEqual(['bubble', buttonElement]);
        });

        it('handle propagation of click events between disjointed roots #2', async () => {
          const buttonRef = React.createRef();
          const button2Ref = React.createRef();
          const divRef = React.createRef();
          const spanRef = React.createRef();
          const log = [];
          const onClick = jest.fn(e => log.push(['bubble', e.currentTarget]));
          const onClickCapture = jest.fn(e =>
            log.push(['capture', e.currentTarget]),
          );

          function Child() {
            return (
              <div
                ref={divRef}
                onClick={onClick}
                onClickCapture={onClickCapture}>
                Click me!
              </div>
            );
          }

          function Parent() {
            return (
              <button
                ref={button2Ref}
                onClick={onClick}
                onClickCapture={onClickCapture}
              />
            );
          }

          function GrandParent() {
            return (
              <button
                ref={buttonRef}
                onClick={onClick}
                onClickCapture={onClickCapture}>
                <span ref={spanRef} />
              </button>
            );
          }

          // We make a wrapper with an inner container that we
          // render to. So it looks like <div><span></span></div>
          // We then render to all three:
          // - container
          // - parentContainer
          // - childContainer

          const parentContainer = document.createElement('div');
          const childContainer = document.createElement('div');

          const root = ReactDOMClient.createRoot(container);
          await act(() => {
            root.render(<GrandParent />);
          });
          const parentRoot = ReactDOMClient.createRoot(parentContainer);
          await act(() => {
            parentRoot.render(<Parent />);
          });
          const childRoot = ReactDOMClient.createRoot(childContainer);
          await act(() => {
            childRoot.render(<Child />);
          });

          parentContainer.appendChild(childContainer);
          spanRef.current.appendChild(parentContainer);

          // Inside <GrandParent />
          const buttonElement = buttonRef.current;
          dispatchClickEvent(buttonElement);
          expect(onClick).toHaveBeenCalledTimes(1);
          expect(onClickCapture).toHaveBeenCalledTimes(1);
          expect(log[0]).toEqual(['capture', buttonElement]);
          expect(log[1]).toEqual(['bubble', buttonElement]);

          // Inside <Child />
          const divElement = divRef.current;
          dispatchClickEvent(divElement);
          expect(onClick).toHaveBeenCalledTimes(3);
          expect(onClickCapture).toHaveBeenCalledTimes(3);
          expect(log[2]).toEqual(['capture', buttonElement]);
          expect(log[3]).toEqual(['capture', divElement]);
          expect(log[4]).toEqual(['bubble', divElement]);
          expect(log[5]).toEqual(['bubble', buttonElement]);

          // Inside <Parent />
          const buttonElement2 = button2Ref.current;
          dispatchClickEvent(buttonElement2);
          expect(onClick).toHaveBeenCalledTimes(5);
          expect(onClickCapture).toHaveBeenCalledTimes(5);
          expect(log[6]).toEqual(['capture', buttonElement]);
          expect(log[7]).toEqual(['capture', buttonElement2]);
          expect(log[8]).toEqual(['bubble', buttonElement2]);
          expect(log[9]).toEqual(['bubble', buttonElement]);
        });

        // @gate !disableCommentsAsDOMContainers
        it('handle propagation of click events between disjointed comment roots', async () => {
          const buttonRef = React.createRef();
          const divRef = React.createRef();
          const log = [];
          const onClick = jest.fn(e => log.push(['bubble', e.currentTarget]));
          const onClickCapture = jest.fn(e =>
            log.push(['capture', e.currentTarget]),
          );

          function Child() {
            return (
              <div
                ref={divRef}
                onClick={onClick}
                onClickCapture={onClickCapture}>
                Click me!
              </div>
            );
          }

          function Parent() {
            return (
              <button
                ref={buttonRef}
                onClick={onClick}
                onClickCapture={onClickCapture}
              />
            );
          }

          // We use a comment node here, then mount to it
          const disjointedNode = document.createComment(
            ' react-mount-point-unstable ',
          );
          const root = ReactDOMClient.createRoot(container);
          await act(() => {
            root.render(<Parent />);
          });
          buttonRef.current.appendChild(disjointedNode);
          const disjointedNodeRoot = ReactDOMClient.createRoot(disjointedNode);
          await act(() => {
            disjointedNodeRoot.render(<Child />);
          });

          const buttonElement = buttonRef.current;
          await act(() => {
            dispatchClickEvent(buttonElement);
          });
          expect(onClick).toHaveBeenCalledTimes(1);
          expect(onClickCapture).toHaveBeenCalledTimes(1);
          expect(log[0]).toEqual(['capture', buttonElement]);
          expect(log[1]).toEqual(['bubble', buttonElement]);

          const divElement = divRef.current;
          await act(() => {
            dispatchClickEvent(divElement);
          });
          expect(onClick).toHaveBeenCalledTimes(3);
          expect(onClickCapture).toHaveBeenCalledTimes(3);
          expect(log[2]).toEqual(['capture', buttonElement]);
          expect(log[3]).toEqual(['capture', divElement]);
          expect(log[4]).toEqual(['bubble', divElement]);
          expect(log[5]).toEqual(['bubble', buttonElement]);
        });

        // @gate !disableCommentsAsDOMContainers
        it('handle propagation of click events between disjointed comment roots #2', async () => {
          const buttonRef = React.createRef();
          const divRef = React.createRef();
          const spanRef = React.createRef();
          const log = [];
          const onClick = jest.fn(e => log.push(['bubble', e.currentTarget]));
          const onClickCapture = jest.fn(e =>
            log.push(['capture', e.currentTarget]),
          );

          function Child() {
            return (
              <div
                ref={divRef}
                onClick={onClick}
                onClickCapture={onClickCapture}>
                Click me!
              </div>
            );
          }

          function Parent() {
            return (
              <button
                ref={buttonRef}
                onClick={onClick}
                onClickCapture={onClickCapture}>
                <span ref={spanRef} />
              </button>
            );
          }

          // We use a comment node here, then mount to it
          const disjointedNode = document.createComment(
            ' react-mount-point-unstable ',
          );
          const root = ReactDOMClient.createRoot(container);
          await act(() => {
            root.render(<Parent />);
          });
          spanRef.current.appendChild(disjointedNode);
          const disjointedNodeRoot = ReactDOMClient.createRoot(disjointedNode);
          await act(() => {
            disjointedNodeRoot.render(<Child />);
          });

          const buttonElement = buttonRef.current;
          await act(() => {
            dispatchClickEvent(buttonElement);
          });
          expect(onClick).toHaveBeenCalledTimes(1);
          expect(onClickCapture).toHaveBeenCalledTimes(1);
          expect(log[0]).toEqual(['capture', buttonElement]);
          expect(log[1]).toEqual(['bubble', buttonElement]);

          const divElement = divRef.current;
          await act(() => {
            dispatchClickEvent(divElement);
          });
          expect(onClick).toHaveBeenCalledTimes(3);
          expect(onClickCapture).toHaveBeenCalledTimes(3);
          expect(log[2]).toEqual(['capture', buttonElement]);
          expect(log[3]).toEqual(['capture', divElement]);
          expect(log[4]).toEqual(['bubble', divElement]);
          expect(log[5]).toEqual(['bubble', buttonElement]);
        });

        it('handle propagation of click events between portals', async () => {
          const buttonRef = React.createRef();
          const divRef = React.createRef();
          const log = [];
          const onClick = jest.fn(e => log.push(['bubble', e.currentTarget]));
          const onClickCapture = jest.fn(e =>
            log.push(['capture', e.currentTarget]),
          );

          const portalElement = document.createElement('div');
          document.body.appendChild(portalElement);

          function Child() {
            return (
              <div
                ref={divRef}
                onClick={onClick}
                onClickCapture={onClickCapture}>
                Click me!
              </div>
            );
          }

          function Parent() {
            return (
              <button
                ref={buttonRef}
                onClick={onClick}
                onClickCapture={onClickCapture}>
                {ReactDOM.createPortal(<Child />, portalElement)}
              </button>
            );
          }

          const root = ReactDOMClient.createRoot(container);
          await act(() => {
            root.render(<Parent />);
          });

          const buttonElement = buttonRef.current;
          dispatchClickEvent(buttonElement);
          expect(onClick).toHaveBeenCalledTimes(1);
          expect(onClickCapture).toHaveBeenCalledTimes(1);
          expect(log[0]).toEqual(['capture', buttonElement]);
          expect(log[1]).toEqual(['bubble', buttonElement]);

          const divElement = divRef.current;
          dispatchClickEvent(divElement);
          expect(onClick).toHaveBeenCalledTimes(3);
          expect(onClickCapture).toHaveBeenCalledTimes(3);
          expect(log[2]).toEqual(['capture', buttonElement]);
          expect(log[3]).toEqual(['capture', divElement]);
          expect(log[4]).toEqual(['bubble', divElement]);
          expect(log[5]).toEqual(['bubble', buttonElement]);

          document.body.removeChild(portalElement);
        });

        it('handle click events on document.body portals', async () => {
          const log = [];

          function Child({label}) {
            return <div onClick={() => log.push(label)}>{label}</div>;
          }

          function Parent() {
            return (
              <>
                {ReactDOM.createPortal(
                  <Child label={'first'} />,
                  document.body,
                )}
                {ReactDOM.createPortal(
                  <Child label={'second'} />,
                  document.body,
                )}
              </>
            );
          }

          const root = ReactDOMClient.createRoot(container);
          await act(() => {
            root.render(<Parent />);
          });

          const second = document.body.lastChild;
          expect(second.textContent).toEqual('second');
          dispatchClickEvent(second);

          expect(log).toEqual(['second']);

          const first = second.previousSibling;
          expect(first.textContent).toEqual('first');
          dispatchClickEvent(first);

          expect(log).toEqual(['second', 'first']);
        });

        it('does not invoke an event on a parent tree when a subtree is dehydrated', async () => {
          let suspend = false;
          let resolve;
          const promise = new Promise(
            resolvePromise => (resolve = resolvePromise),
          );

          let clicks = 0;
          const childSlotRef = React.createRef();

          function Parent() {
            return <div onClick={() => clicks++} ref={childSlotRef} />;
          }

          function Child({text}) {
            if (suspend) {
              throw promise;
            } else {
              return <a>Click me</a>;
            }
          }

          function App() {
            // The root is a Suspense boundary.
            return (
              <React.Suspense fallback="Loading...">
                <Child />
              </React.Suspense>
            );
          }

          suspend = false;
          const finalHTML = ReactDOMServer.renderToString(<App />);

          const parentContainer = document.createElement('div');
          const childContainer = document.createElement('div');

          // We need this to be in the document since we'll dispatch events on it.
          document.body.appendChild(parentContainer);

          // We're going to use a different root as a parent.
          // This lets us detect whether an event goes through React's event system.
          const parentRoot = ReactDOMClient.createRoot(parentContainer);
          await act(() => {
            parentRoot.render(<Parent />);
          });

          childSlotRef.current.appendChild(childContainer);

          childContainer.innerHTML = finalHTML;

          const a = childContainer.getElementsByTagName('a')[0];

          suspend = true;

          // Hydrate asynchronously.
          await act(() => {
            ReactDOMClient.hydrateRoot(childContainer, <App />);
          });

          // The Suspense boundary is not yet hydrated.
          await act(() => {
            a.click();
          });
          expect(clicks).toBe(0);

          // Resolving the promise so that rendering can complete.
          await act(async () => {
            suspend = false;
            resolve();
            await promise;
          });

          // We're now full hydrated.
          expect(clicks).toBe(0);
          document.body.removeChild(parentContainer);
        });

        it('handle click events on dynamic portals', async () => {
          const log = [];

          function Parent() {
            const ref = React.useRef(null);
            const [portal, setPortal] = React.useState(null);

            React.useEffect(() => {
              setPortal(
                ReactDOM.createPortal(
                  <span onClick={() => log.push('child')} id="child" />,
                  ref.current,
                ),
              );
            }, []);

            return (
              <div ref={ref} onClick={() => log.push('parent')} id="parent">
                {portal}
              </div>
            );
          }

          const root = ReactDOMClient.createRoot(container);
          await act(() => {
            root.render(<Parent />);
          });

          const parent = container.lastChild;
          expect(parent.id).toEqual('parent');

          await act(() => {
            dispatchClickEvent(parent);
          });

          expect(log).toEqual(['parent']);

          const child = parent.lastChild;
          expect(child.id).toEqual('child');

          await act(() => {
            dispatchClickEvent(child);
          });

          // we add both 'child' and 'parent' due to bubbling
          expect(log).toEqual(['parent', 'child', 'parent']);
        });

        // Slight alteration to the last test, to catch
        // a subtle difference in traversal.
        it('handle click events on dynamic portals #2', async () => {
          const log = [];

          function Parent() {
            const ref = React.useRef(null);
            const [portal, setPortal] = React.useState(null);

            React.useEffect(() => {
              setPortal(
                ReactDOM.createPortal(
                  <span onClick={() => log.push('child')} id="child" />,
                  ref.current,
                ),
              );
            }, []);

            return (
              <div ref={ref} onClick={() => log.push('parent')} id="parent">
                <div>{portal}</div>
              </div>
            );
          }

          const root = ReactDOMClient.createRoot(container);
          await act(() => {
            root.render(<Parent />);
          });

          const parent = container.lastChild;
          expect(parent.id).toEqual('parent');

          await act(() => {
            dispatchClickEvent(parent);
          });

          expect(log).toEqual(['parent']);

          const child = parent.lastChild;
          expect(child.id).toEqual('child');

          await act(() => {
            dispatchClickEvent(child);
          });

          // we add both 'child' and 'parent' due to bubbling
          expect(log).toEqual(['parent', 'child', 'parent']);
        });

        it('native stopPropagation on click events between portals', async () => {
          const buttonRef = React.createRef();
          const divRef = React.createRef();
          const middleDivRef = React.createRef();
          const log = [];
          const onClick = jest.fn(e => log.push(['bubble', e.currentTarget]));
          const onClickCapture = jest.fn(e =>
            log.push(['capture', e.currentTarget]),
          );

          const portalElement = document.createElement('div');
          document.body.appendChild(portalElement);

          function Child() {
            return (
              <div ref={middleDivRef}>
                <div
                  ref={divRef}
                  onClick={onClick}
                  onClickCapture={onClickCapture}>
                  Click me!
                </div>
              </div>
            );
          }

          function Parent() {
            React.useLayoutEffect(() => {
              // This should prevent the portalElement listeners from
              // capturing the events in the bubble phase.
              middleDivRef.current.addEventListener('click', e => {
                e.stopPropagation();
              });
            });

            return (
              <button
                ref={buttonRef}
                onClick={onClick}
                onClickCapture={onClickCapture}>
                {ReactDOM.createPortal(<Child />, portalElement)}
              </button>
            );
          }

          const root = ReactDOMClient.createRoot(container);
          await act(() => {
            root.render(<Parent />);
          });

          const buttonElement = buttonRef.current;
          dispatchClickEvent(buttonElement);
          expect(onClick).toHaveBeenCalledTimes(1);
          expect(onClickCapture).toHaveBeenCalledTimes(1);
          expect(log[0]).toEqual(['capture', buttonElement]);
          expect(log[1]).toEqual(['bubble', buttonElement]);

          const divElement = divRef.current;
          dispatchClickEvent(divElement);
          expect(onClick).toHaveBeenCalledTimes(1);
          expect(onClickCapture).toHaveBeenCalledTimes(3);

          document.body.removeChild(portalElement);
        });

        it('handle propagation of focus events', async () => {
          const buttonRef = React.createRef();
          const divRef = React.createRef();
          const log = [];
          const onFocus = jest.fn(e => log.push(['bubble', e.currentTarget]));
          const onFocusCapture = jest.fn(e =>
            log.push(['capture', e.currentTarget]),
          );

          function Test() {
            return (
              <button
                ref={buttonRef}
                onFocus={onFocus}
                onFocusCapture={onFocusCapture}>
                <div
                  ref={divRef}
                  onFocus={onFocus}
                  onFocusCapture={onFocusCapture}
                  tabIndex={0}>
                  Click me!
                </div>
              </button>
            );
          }

          const root = ReactDOMClient.createRoot(container);
          await act(() => {
            root.render(<Test />);
          });

          const buttonElement = buttonRef.current;
          buttonElement.focus();
          expect(onFocus).toHaveBeenCalledTimes(1);
          expect(onFocusCapture).toHaveBeenCalledTimes(1);
          expect(log[0]).toEqual(['capture', buttonElement]);
          expect(log[1]).toEqual(['bubble', buttonElement]);

          const divElement = divRef.current;
          divElement.focus();
          expect(onFocus).toHaveBeenCalledTimes(3);
          expect(onFocusCapture).toHaveBeenCalledTimes(3);
          expect(log[2]).toEqual(['capture', buttonElement]);
          expect(log[3]).toEqual(['capture', divElement]);
          expect(log[4]).toEqual(['bubble', divElement]);
          expect(log[5]).toEqual(['bubble', buttonElement]);
        });

        it('handle propagation of focus events between roots', async () => {
          const buttonRef = React.createRef();
          const divRef = React.createRef();
          const childRef = React.createRef();
          const log = [];
          const onFocus = jest.fn(e => log.push(['bubble', e.currentTarget]));
          const onFocusCapture = jest.fn(e =>
            log.push(['capture', e.currentTarget]),
          );

          function Child() {
            return (
              <div
                ref={divRef}
                onFocus={onFocus}
                onFocusCapture={onFocusCapture}
                tabIndex={0}>
                Click me!
              </div>
            );
          }

          function Parent() {
            return (
              <button
                ref={buttonRef}
                onFocus={onFocus}
                onFocusCapture={onFocusCapture}>
                <div ref={childRef} />
              </button>
            );
          }

          const root = ReactDOMClient.createRoot(container);
          await act(() => {
            root.render(<Parent />);
          });
          const childRoot = ReactDOMClient.createRoot(childRef.current);
          await act(() => {
            childRoot.render(<Child />);
          });

          const buttonElement = buttonRef.current;
          buttonElement.focus();
          expect(onFocus).toHaveBeenCalledTimes(1);
          expect(onFocusCapture).toHaveBeenCalledTimes(1);
          expect(log[0]).toEqual(['capture', buttonElement]);
          expect(log[1]).toEqual(['bubble', buttonElement]);

          const divElement = divRef.current;
          divElement.focus();
          expect(onFocus).toHaveBeenCalledTimes(3);
          expect(onFocusCapture).toHaveBeenCalledTimes(3);
          expect(log[2]).toEqual(['capture', buttonElement]);
          expect(log[3]).toEqual(['capture', divElement]);
          expect(log[4]).toEqual(['bubble', divElement]);
          expect(log[5]).toEqual(['bubble', buttonElement]);
        });

        it('handle propagation of focus events between portals', async () => {
          const buttonRef = React.createRef();
          const divRef = React.createRef();
          const log = [];
          const onFocus = jest.fn(e => log.push(['bubble', e.currentTarget]));
          const onFocusCapture = jest.fn(e =>
            log.push(['capture', e.currentTarget]),
          );

          const portalElement = document.createElement('div');
          document.body.appendChild(portalElement);

          function Child() {
            return (
              <div
                ref={divRef}
                onFocus={onFocus}
                onFocusCapture={onFocusCapture}
                tabIndex={0}>
                Click me!
              </div>
            );
          }

          function Parent() {
            return (
              <button
                ref={buttonRef}
                onFocus={onFocus}
                onFocusCapture={onFocusCapture}>
                {ReactDOM.createPortal(<Child />, portalElement)}
              </button>
            );
          }

          const root = ReactDOMClient.createRoot(container);
          await act(() => {
            root.render(<Parent />);
          });

          const buttonElement = buttonRef.current;
          buttonElement.focus();
          expect(onFocus).toHaveBeenCalledTimes(1);
          expect(onFocusCapture).toHaveBeenCalledTimes(1);
          expect(log[0]).toEqual(['capture', buttonElement]);
          expect(log[1]).toEqual(['bubble', buttonElement]);

          const divElement = divRef.current;
          divElement.focus();
          expect(onFocus).toHaveBeenCalledTimes(3);
          expect(onFocusCapture).toHaveBeenCalledTimes(3);
          expect(log[2]).toEqual(['capture', buttonElement]);
          expect(log[3]).toEqual(['capture', divElement]);
          expect(log[4]).toEqual(['bubble', divElement]);
          expect(log[5]).toEqual(['bubble', buttonElement]);

          document.body.removeChild(portalElement);
        });

        it('native stopPropagation on focus events between portals', async () => {
          const buttonRef = React.createRef();
          const divRef = React.createRef();
          const middleDivRef = React.createRef();
          const log = [];
          const onFocus = jest.fn(e => log.push(['bubble', e.currentTarget]));
          const onFocusCapture = jest.fn(e =>
            log.push(['capture', e.currentTarget]),
          );

          const portalElement = document.createElement('div');
          document.body.appendChild(portalElement);

          function Child() {
            return (
              <div ref={middleDivRef}>
                <div
                  ref={divRef}
                  onFocus={onFocus}
                  onFocusCapture={onFocusCapture}
                  tabIndex={0}>
                  Click me!
                </div>
              </div>
            );
          }

          function Parent() {
            React.useLayoutEffect(() => {
              // This should prevent the portalElement listeners from
              // capturing the events in the bubble phase.
              middleDivRef.current.addEventListener('focusin', e => {
                e.stopPropagation();
              });
            });

            return (
              <button
                ref={buttonRef}
                onFocus={onFocus}
                onFocusCapture={onFocusCapture}>
                {ReactDOM.createPortal(<Child />, portalElement)}
              </button>
            );
          }

          const root = ReactDOMClient.createRoot(container);
          await act(() => {
            root.render(<Parent />);
          });

          const buttonElement = buttonRef.current;
          buttonElement.focus();
          expect(onFocus).toHaveBeenCalledTimes(1);
          expect(onFocusCapture).toHaveBeenCalledTimes(1);
          expect(log[0]).toEqual(['capture', buttonElement]);
          expect(log[1]).toEqual(['bubble', buttonElement]);

          const divElement = divRef.current;
          divElement.focus();
          expect(onFocus).toHaveBeenCalledTimes(1);
          expect(onFocusCapture).toHaveBeenCalledTimes(3);

          document.body.removeChild(portalElement);
        });

        it('handle propagation of enter and leave events between portals', async () => {
          const buttonRef = React.createRef();
          const divRef = React.createRef();
          const log = [];
          const onMouseEnter = jest.fn(e => log.push(e.currentTarget));
          const onMouseLeave = jest.fn(e => log.push(e.currentTarget));

          const portalElement = document.createElement('div');
          document.body.appendChild(portalElement);

          function Child() {
            return (
              <div
                ref={divRef}
                onMouseEnter={onMouseEnter}
                onMouseLeave={onMouseLeave}
              />
            );
          }

          function Parent() {
            return (
              <button
                ref={buttonRef}
                onMouseEnter={onMouseEnter}
                onMouseLeave={onMouseLeave}>
                {ReactDOM.createPortal(<Child />, portalElement)}
              </button>
            );
          }

          const root = ReactDOMClient.createRoot(container);
          await act(() => {
            root.render(<Parent />);
          });

          const buttonElement = buttonRef.current;
          buttonElement.dispatchEvent(
            new MouseEvent('mouseover', {
              bubbles: true,
              cancelable: true,
              relatedTarget: null,
            }),
          );
          expect(onMouseEnter).toHaveBeenCalledTimes(1);
          expect(onMouseLeave).toHaveBeenCalledTimes(0);
          expect(log[0]).toEqual(buttonElement);

          const divElement = divRef.current;
          buttonElement.dispatchEvent(
            new MouseEvent('mouseout', {
              bubbles: true,
              cancelable: true,
              relatedTarget: divElement,
            }),
          );
          divElement.dispatchEvent(
            new MouseEvent('mouseover', {
              bubbles: true,
              cancelable: true,
              relatedTarget: buttonElement,
            }),
          );
          expect(onMouseEnter).toHaveBeenCalledTimes(2);
          expect(onMouseLeave).toHaveBeenCalledTimes(0);
          expect(log[1]).toEqual(divElement);

          document.body.removeChild(portalElement);
        });

        it('handle propagation of enter and leave events between portals #2', async () => {
          const buttonRef = React.createRef();
          const divRef = React.createRef();
          const portalRef = React.createRef();
          const log = [];
          const onMouseEnter = jest.fn(e => log.push(e.currentTarget));
          const onMouseLeave = jest.fn(e => log.push(e.currentTarget));

          function Child() {
            return (
              <div
                ref={divRef}
                onMouseEnter={onMouseEnter}
                onMouseLeave={onMouseLeave}
              />
            );
          }

          function Parent() {
            const [portal, setPortal] = React.useState(null);

            React.useLayoutEffect(() => {
              setPortal(ReactDOM.createPortal(<Child />, portalRef.current));
            }, []);

            return (
              <button
                ref={buttonRef}
                onMouseEnter={onMouseEnter}
                onMouseLeave={onMouseLeave}>
                <div ref={portalRef}>{portal}</div>
              </button>
            );
          }

          const root = ReactDOMClient.createRoot(container);
          await act(() => {
            root.render(<Parent />);
          });

          const buttonElement = buttonRef.current;
          buttonElement.dispatchEvent(
            new MouseEvent('mouseover', {
              bubbles: true,
              cancelable: true,
              relatedTarget: null,
            }),
          );
          expect(onMouseEnter).toHaveBeenCalledTimes(1);
          expect(onMouseLeave).toHaveBeenCalledTimes(0);
          expect(log[0]).toEqual(buttonElement);

          const divElement = divRef.current;
          buttonElement.dispatchEvent(
            new MouseEvent('mouseout', {
              bubbles: true,
              cancelable: true,
              relatedTarget: divElement,
            }),
          );
          divElement.dispatchEvent(
            new MouseEvent('mouseover', {
              bubbles: true,
              cancelable: true,
              relatedTarget: buttonElement,
            }),
          );
          expect(onMouseEnter).toHaveBeenCalledTimes(2);
          expect(onMouseLeave).toHaveBeenCalledTimes(0);
          expect(log[1]).toEqual(divElement);
        });

        it('should preserve bubble/capture order between roots and nested portals', async () => {
          const targetRef = React.createRef();
          let log = [];
          const onClickRoot = jest.fn(e => log.push('bubble root'));
          const onClickCaptureRoot = jest.fn(e => log.push('capture root'));
          const onClickPortal = jest.fn(e => log.push('bubble portal'));
          const onClickCapturePortal = jest.fn(e => log.push('capture portal'));

          function Portal() {
            return (
              <div
                onClick={onClickPortal}
                onClickCapture={onClickCapturePortal}
                ref={targetRef}>
                Click me!
              </div>
            );
          }

          const portalContainer = document.createElement('div');

          let shouldStopPropagation = false;
          portalContainer.addEventListener(
            'click',
            e => {
              if (shouldStopPropagation) {
                e.stopPropagation();
              }
            },
            false,
          );

          function Root() {
            const portalTargetRef = React.useRef(null);
            React.useLayoutEffect(() => {
              portalTargetRef.current.appendChild(portalContainer);
            });
            return (
              <div onClick={onClickRoot} onClickCapture={onClickCaptureRoot}>
                <div ref={portalTargetRef} />
                {ReactDOM.createPortal(<Portal />, portalContainer)}
              </div>
            );
          }

          const root = ReactDOMClient.createRoot(container);
          await act(() => {
            root.render(<Root />);
          });

          const divElement = targetRef.current;
          dispatchClickEvent(divElement);
          expect(log).toEqual([
            'capture root',
            'capture portal',
            'bubble portal',
            'bubble root',
          ]);

          log = [];

          shouldStopPropagation = true;
          dispatchClickEvent(divElement);

          if (enableLegacyFBSupport) {
            // We aren't using roots with legacyFBSupport, we put clicks on the document, so we exbit the previous
            // behavior.
            expect(log).toEqual(['capture root', 'capture portal']);
          } else {
            expect(log).toEqual([
              // The events on root probably shouldn't fire if a non-React intermediated. but current behavior is that they do.
              'capture root',
              'capture portal',
              'bubble portal',
              'bubble root',
            ]);
          }
        });

        describe('ReactDOM.createEventHandle', () => {
          beforeEach(() => {
            jest.resetModules();
            ReactFeatureFlags = require('shared/ReactFeatureFlags');
            ReactFeatureFlags.enableLegacyFBSupport = enableLegacyFBSupport;
            ReactFeatureFlags.enableCreateEventHandleAPI = true;

            React = require('react');
            ReactDOM = require('react-dom');
            ReactDOMClient = require('react-dom/client');
            Scheduler = require('scheduler');
            ReactDOMServer = require('react-dom/server');
            act = require('internal-test-utils').act;

            const InternalTestUtils = require('internal-test-utils');
            waitForAll = InternalTestUtils.waitForAll;
            waitFor = InternalTestUtils.waitFor;
          });

          // @gate www
          it('can render correctly with the ReactDOMServer', () => {
            const clickEvent = jest.fn();
            const setClick = ReactDOM.unstable_createEventHandle('click');

            function Test() {
              const divRef = React.useRef(null);

              React.useEffect(() => {
                return setClick(divRef.current, clickEvent);
              });

              return <div ref={divRef}>Hello world</div>;
            }
            const output = ReactDOMServer.renderToString(<Test />);
            expect(output).toBe(`<div>Hello world</div>`);
          });

          // @gate www
          it('can render correctly with the ReactDOMServer hydration', async () => {
            const clickEvent = jest.fn();
            const spanRef = React.createRef();
            const setClick = ReactDOM.unstable_createEventHandle('click');

            function Test() {
              React.useEffect(() => {
                return setClick(spanRef.current, clickEvent);
              });

              return (
                <div>
                  <span ref={spanRef}>Hello world</span>
                </div>
              );
            }
            const output = ReactDOMServer.renderToString(<Test />);
            expect(output).toBe(`<div><span>Hello world</span></div>`);
            container.innerHTML = output;
            await act(() => {
              ReactDOMClient.hydrateRoot(container, <Test />);
            });
            dispatchClickEvent(spanRef.current);
            expect(clickEvent).toHaveBeenCalledTimes(1);
          });

          // @gate www
          it('should correctly work for a basic "click" listener', async () => {
            let log = [];
            const clickEvent = jest.fn(event => {
              log.push({
                eventPhase: event.eventPhase,
                type: event.type,
                currentTarget: event.currentTarget,
                target: event.target,
              });
            });
            const divRef = React.createRef();
            const buttonRef = React.createRef();
            const setClick = ReactDOM.unstable_createEventHandle('click');

            function Test() {
              React.useEffect(() => {
                return setClick(buttonRef.current, clickEvent);
              });

              return (
                <button ref={buttonRef}>
                  <div ref={divRef}>Click me!</div>
                </button>
              );
            }

            const root = ReactDOMClient.createRoot(container);
            await act(() => {
              root.render(<Test />);
            });

            expect(container.innerHTML).toBe(
              '<button><div>Click me!</div></button>',
            );

            // Clicking the button should trigger the event callback
            let divElement = divRef.current;
            dispatchClickEvent(divElement);
            expect(log).toEqual([
              {
                eventPhase: 3,
                type: 'click',
                currentTarget: buttonRef.current,
                target: divRef.current,
              },
            ]);
            expect(clickEvent).toBeCalledTimes(1);

            // Unmounting the container and clicking should not work
            await act(() => {
              root.render(null);
            });

            dispatchClickEvent(divElement);
            expect(clickEvent).toBeCalledTimes(1);

            // Re-rendering the container and clicking should work
            await act(() => {
              root.render(<Test />);
            });

            divElement = divRef.current;
            dispatchClickEvent(divElement);
            expect(clickEvent).toBeCalledTimes(2);

            log = [];

            // Clicking the button should also work
            const buttonElement = buttonRef.current;
            dispatchClickEvent(buttonElement);
            expect(log).toEqual([
              {
                eventPhase: 3,
                type: 'click',
                currentTarget: buttonRef.current,
                target: buttonRef.current,
              },
            ]);

            const setClick2 = ReactDOM.unstable_createEventHandle('click');

            function Test2({clickEvent2}) {
              React.useEffect(() => {
                return setClick2(buttonRef.current, clickEvent2);
              });

              return (
                <button ref={buttonRef}>
                  <div ref={divRef}>Click me!</div>
                </button>
              );
            }

            let clickEvent2 = jest.fn();
            await act(() => {
              root.render(<Test2 clickEvent2={clickEvent2} />);
            });

            divElement = divRef.current;
            dispatchClickEvent(divElement);
            expect(clickEvent2).toBeCalledTimes(1);

            // Reset the function we pass in, so it's different
            clickEvent2 = jest.fn();
            await act(() => {
              root.render(<Test2 clickEvent2={clickEvent2} />);
            });

            divElement = divRef.current;
            dispatchClickEvent(divElement);
            expect(clickEvent2).toBeCalledTimes(1);
          });

          // @gate www
          it('should correctly work for setting and clearing a basic "click" listener', async () => {
            const clickEvent = jest.fn();
            const divRef = React.createRef();
            const buttonRef = React.createRef();
            const setClick = ReactDOM.unstable_createEventHandle('click');

            function Test({off}) {
              React.useEffect(() => {
                const clear = setClick(buttonRef.current, clickEvent);
                if (off) {
                  clear();
                }
                return clear;
              });

              return (
                <button ref={buttonRef}>
                  <div ref={divRef}>Click me!</div>
                </button>
              );
            }

            const root = ReactDOMClient.createRoot(container);

            await act(() => {
              root.render(<Test off={false} />);
            });

            let divElement = divRef.current;
            dispatchClickEvent(divElement);
            expect(clickEvent).toBeCalledTimes(1);

            // The listener should get unmounted
            await act(() => {
              root.render(<Test off={true} />);
            });

            clickEvent.mockClear();

            divElement = divRef.current;
            dispatchClickEvent(divElement);
            expect(clickEvent).toBeCalledTimes(0);
          });

          // @gate www
          it('should handle the target being a text node', async () => {
            const clickEvent = jest.fn();
            const buttonRef = React.createRef();
            const setClick = ReactDOM.unstable_createEventHandle('click');

            function Test() {
              React.useEffect(() => {
                return setClick(buttonRef.current, clickEvent);
              });

              return <button ref={buttonRef}>Click me!</button>;
            }

            const root = ReactDOMClient.createRoot(container);
            await act(() => {
              root.render(<Test />);
            });

            const textNode = buttonRef.current.firstChild;
            dispatchClickEvent(textNode);
            expect(clickEvent).toBeCalledTimes(1);
          });

          // @gate www
          it('handle propagation of click events', async () => {
            const buttonRef = React.createRef();
            const divRef = React.createRef();
            const log = [];
            const onClick = jest.fn(e => log.push(['bubble', e.currentTarget]));
            const onClickCapture = jest.fn(e =>
              log.push(['capture', e.currentTarget]),
            );
            const setClick = ReactDOM.unstable_createEventHandle('click');
            const setCaptureClick = ReactDOM.unstable_createEventHandle(
              'click',
              {
                capture: true,
              },
            );

            function Test() {
              React.useEffect(() => {
                const clearClick1 = setClick(buttonRef.current, onClick);
                const clearCaptureClick1 = setCaptureClick(
                  buttonRef.current,
                  onClickCapture,
                );
                const clearClick2 = setClick(divRef.current, onClick);
                const clearCaptureClick2 = setCaptureClick(
                  divRef.current,
                  onClickCapture,
                );

                return () => {
                  clearClick1();
                  clearCaptureClick1();
                  clearClick2();
                  clearCaptureClick2();
                };
              });

              return (
                <button ref={buttonRef}>
                  <div ref={divRef}>Click me!</div>
                </button>
              );
            }

            const root = ReactDOMClient.createRoot(container);
            await act(() => {
              root.render(<Test />);
            });

            const buttonElement = buttonRef.current;
            dispatchClickEvent(buttonElement);
            expect(onClick).toHaveBeenCalledTimes(1);
            expect(onClickCapture).toHaveBeenCalledTimes(1);
            expect(log[0]).toEqual(['capture', buttonElement]);
            expect(log[1]).toEqual(['bubble', buttonElement]);

            log.length = 0;
            onClick.mockClear();
            onClickCapture.mockClear();

            const divElement = divRef.current;
            dispatchClickEvent(divElement);
            expect(onClick).toHaveBeenCalledTimes(2);
            expect(onClickCapture).toHaveBeenCalledTimes(2);
            expect(log[0]).toEqual(['capture', buttonElement]);
            expect(log[1]).toEqual(['capture', divElement]);
            expect(log[2]).toEqual(['bubble', divElement]);
            expect(log[3]).toEqual(['bubble', buttonElement]);
          });

          // @gate www
          it('handle propagation of click events mixed with onClick events', async () => {
            const buttonRef = React.createRef();
            const divRef = React.createRef();
            const log = [];
            const onClick = jest.fn(e => log.push(['bubble', e.currentTarget]));
            const onClickCapture = jest.fn(e =>
              log.push(['capture', e.currentTarget]),
            );
            const setClick = ReactDOM.unstable_createEventHandle('click');
            const setClickCapture = ReactDOM.unstable_createEventHandle(
              'click',
              {
                capture: true,
              },
            );

            function Test() {
              React.useEffect(() => {
                setClick(buttonRef.current, onClick);
                setClickCapture(buttonRef.current, onClickCapture);

                return () => {
                  setClick();
                  setClickCapture();
                };
              });

              return (
                <button ref={buttonRef}>
                  <div
                    ref={divRef}
                    onClick={onClick}
                    onClickCapture={onClickCapture}>
                    Click me!
                  </div>
                </button>
              );
            }

            const root = ReactDOMClient.createRoot(container);
            await act(() => {
              root.render(<Test />);
            });

            const buttonElement = buttonRef.current;
            dispatchClickEvent(buttonElement);
            expect(onClick).toHaveBeenCalledTimes(1);
            expect(onClickCapture).toHaveBeenCalledTimes(1);
            expect(log[0]).toEqual(['capture', buttonElement]);
            expect(log[1]).toEqual(['bubble', buttonElement]);

            const divElement = divRef.current;
            dispatchClickEvent(divElement);
            expect(onClick).toHaveBeenCalledTimes(3);
            expect(onClickCapture).toHaveBeenCalledTimes(3);
            expect(log[2]).toEqual(['capture', buttonElement]);
            expect(log[3]).toEqual(['capture', divElement]);
            expect(log[4]).toEqual(['bubble', divElement]);
            expect(log[5]).toEqual(['bubble', buttonElement]);
          });

          // @gate www
          it('should correctly work for a basic "click" listener on the outer target', async () => {
            const log = [];
            const clickEvent = jest.fn(event => {
              log.push({
                eventPhase: event.eventPhase,
                type: event.type,
                currentTarget: event.currentTarget,
                target: event.target,
              });
            });
            const divRef = React.createRef();
            const buttonRef = React.createRef();
            const setClick = ReactDOM.unstable_createEventHandle('click');

            function Test() {
              React.useEffect(() => {
                return setClick(divRef.current, clickEvent);
              });

              return (
                <button ref={buttonRef}>
                  <div ref={divRef}>Click me!</div>
                </button>
              );
            }

            const root = ReactDOMClient.createRoot(container);
            await act(() => {
              root.render(<Test />);
            });

            expect(container.innerHTML).toBe(
              '<button><div>Click me!</div></button>',
            );

            // Clicking the button should trigger the event callback
            let divElement = divRef.current;
            dispatchClickEvent(divElement);
            expect(log).toEqual([
              {
                eventPhase: 3,
                type: 'click',
                currentTarget: divRef.current,
                target: divRef.current,
              },
            ]);

            // Unmounting the container and clicking should not work
            await act(() => {
              root.render(null);
            });

            dispatchClickEvent(divElement);
            expect(clickEvent).toBeCalledTimes(1);

            // Re-rendering the container and clicking should work
            await act(() => {
              root.render(<Test />);
            });

            divElement = divRef.current;
            dispatchClickEvent(divElement);
            expect(clickEvent).toBeCalledTimes(2);

            // Clicking the button should not work
            const buttonElement = buttonRef.current;
            dispatchClickEvent(buttonElement);
            expect(clickEvent).toBeCalledTimes(2);
          });

          // @gate www
          it('should correctly handle many nested target listeners', async () => {
            const buttonRef = React.createRef();
            const targetListener1 = jest.fn();
            const targetListener2 = jest.fn();
            const targetListener3 = jest.fn();
            const targetListener4 = jest.fn();
            let setClick1 = ReactDOM.unstable_createEventHandle('click', {
              capture: true,
            });
            let setClick2 = ReactDOM.unstable_createEventHandle('click', {
              capture: true,
            });
            let setClick3 = ReactDOM.unstable_createEventHandle('click');
            let setClick4 = ReactDOM.unstable_createEventHandle('click');

            function Test() {
              React.useEffect(() => {
                const clearClick1 = setClick1(
                  buttonRef.current,
                  targetListener1,
                );
                const clearClick2 = setClick2(
                  buttonRef.current,
                  targetListener2,
                );
                const clearClick3 = setClick3(
                  buttonRef.current,
                  targetListener3,
                );
                const clearClick4 = setClick4(
                  buttonRef.current,
                  targetListener4,
                );

                return () => {
                  clearClick1();
                  clearClick2();
                  clearClick3();
                  clearClick4();
                };
              });

              return <button ref={buttonRef}>Click me!</button>;
            }

            const root = ReactDOMClient.createRoot(container);
            await act(() => {
              root.render(<Test />);
            });

            let buttonElement = buttonRef.current;
            dispatchClickEvent(buttonElement);

            expect(targetListener1).toHaveBeenCalledTimes(1);
            expect(targetListener2).toHaveBeenCalledTimes(1);
            expect(targetListener3).toHaveBeenCalledTimes(1);
            expect(targetListener4).toHaveBeenCalledTimes(1);

            setClick1 = ReactDOM.unstable_createEventHandle('click');
            setClick2 = ReactDOM.unstable_createEventHandle('click');
            setClick3 = ReactDOM.unstable_createEventHandle('click');
            setClick4 = ReactDOM.unstable_createEventHandle('click');

            function Test2() {
              React.useEffect(() => {
                const clearClick1 = setClick1(
                  buttonRef.current,
                  targetListener1,
                );
                const clearClick2 = setClick2(
                  buttonRef.current,
                  targetListener2,
                );
                const clearClick3 = setClick3(
                  buttonRef.current,
                  targetListener3,
                );
                const clearClick4 = setClick4(
                  buttonRef.current,
                  targetListener4,
                );

                return () => {
                  clearClick1();
                  clearClick2();
                  clearClick3();
                  clearClick4();
                };
              });

              return <button ref={buttonRef}>Click me!</button>;
            }

            await act(() => {
              root.render(<Test2 />);
            });

            buttonElement = buttonRef.current;
            dispatchClickEvent(buttonElement);
            expect(targetListener1).toHaveBeenCalledTimes(2);
            expect(targetListener2).toHaveBeenCalledTimes(2);
            expect(targetListener3).toHaveBeenCalledTimes(2);
            expect(targetListener4).toHaveBeenCalledTimes(2);
          });

          // @gate www
          it('should correctly handle stopPropagation correctly for target events', async () => {
            const buttonRef = React.createRef();
            const divRef = React.createRef();
            const clickEvent = jest.fn();
            const setClick1 = ReactDOM.unstable_createEventHandle('click', {
              bind: buttonRef,
            });
            const setClick2 = ReactDOM.unstable_createEventHandle('click');

            function Test() {
              React.useEffect(() => {
                const clearClick1 = setClick1(buttonRef.current, clickEvent);
                const clearClick2 = setClick2(divRef.current, e => {
                  e.stopPropagation();
                });

                return () => {
                  clearClick1();
                  clearClick2();
                };
              });

              return (
                <button ref={buttonRef}>
                  <div ref={divRef}>Click me!</div>
                </button>
              );
            }

            const root = ReactDOMClient.createRoot(container);
            await act(() => {
              root.render(<Test />);
            });

            const divElement = divRef.current;
            dispatchClickEvent(divElement);
            expect(clickEvent).toHaveBeenCalledTimes(0);
          });

          // @gate www
          it('should correctly handle stopPropagation correctly for many target events', async () => {
            const buttonRef = React.createRef();
            const targetListener1 = jest.fn(e => e.stopPropagation());
            const targetListener2 = jest.fn(e => e.stopPropagation());
            const targetListener3 = jest.fn(e => e.stopPropagation());
            const targetListener4 = jest.fn(e => e.stopPropagation());
            const setClick1 = ReactDOM.unstable_createEventHandle('click');
            const setClick2 = ReactDOM.unstable_createEventHandle('click');
            const setClick3 = ReactDOM.unstable_createEventHandle('click');
            const setClick4 = ReactDOM.unstable_createEventHandle('click');

            function Test() {
              React.useEffect(() => {
                const clearClick1 = setClick1(
                  buttonRef.current,
                  targetListener1,
                );
                const clearClick2 = setClick2(
                  buttonRef.current,
                  targetListener2,
                );
                const clearClick3 = setClick3(
                  buttonRef.current,
                  targetListener3,
                );
                const clearClick4 = setClick4(
                  buttonRef.current,
                  targetListener4,
                );

                return () => {
                  clearClick1();
                  clearClick2();
                  clearClick3();
                  clearClick4();
                };
              });

              return <button ref={buttonRef}>Click me!</button>;
            }

            const root = ReactDOMClient.createRoot(container);
            await act(() => {
              root.render(<Test />);
            });

            const buttonElement = buttonRef.current;
            dispatchClickEvent(buttonElement);
            expect(targetListener1).toHaveBeenCalledTimes(1);
            expect(targetListener2).toHaveBeenCalledTimes(1);
            expect(targetListener3).toHaveBeenCalledTimes(1);
            expect(targetListener4).toHaveBeenCalledTimes(1);
          });

          // @gate www
          it('should correctly handle stopPropagation for mixed capture/bubbling target listeners', async () => {
            const buttonRef = React.createRef();
            const targetListener1 = jest.fn(e => e.stopPropagation());
            const targetListener2 = jest.fn(e => e.stopPropagation());
            const targetListener3 = jest.fn(e => e.stopPropagation());
            const targetListener4 = jest.fn(e => e.stopPropagation());
            const setClick1 = ReactDOM.unstable_createEventHandle('click', {
              capture: true,
            });
            const setClick2 = ReactDOM.unstable_createEventHandle('click', {
              capture: true,
            });
            const setClick3 = ReactDOM.unstable_createEventHandle('click');
            const setClick4 = ReactDOM.unstable_createEventHandle('click');

            function Test() {
              React.useEffect(() => {
                const clearClick1 = setClick1(
                  buttonRef.current,
                  targetListener1,
                );
                const clearClick2 = setClick2(
                  buttonRef.current,
                  targetListener2,
                );
                const clearClick3 = setClick3(
                  buttonRef.current,
                  targetListener3,
                );
                const clearClick4 = setClick4(
                  buttonRef.current,
                  targetListener4,
                );

                return () => {
                  clearClick1();
                  clearClick2();
                  clearClick3();
                  clearClick4();
                };
              });

              return <button ref={buttonRef}>Click me!</button>;
            }

            const root = ReactDOMClient.createRoot(container);
            await act(() => {
              root.render(<Test />);
            });

            const buttonElement = buttonRef.current;
            dispatchClickEvent(buttonElement);
            expect(targetListener1).toHaveBeenCalledTimes(1);
            expect(targetListener2).toHaveBeenCalledTimes(1);
            expect(targetListener3).toHaveBeenCalledTimes(0);
            expect(targetListener4).toHaveBeenCalledTimes(0);
          });

          // @gate www
          it('should work with concurrent mode updates', async () => {
            const log = [];
            const ref = React.createRef();
            const setClick1 = ReactDOM.unstable_createEventHandle('click');

            function Test({counter}) {
              React.useLayoutEffect(() => {
                return setClick1(ref.current, () => {
                  log.push({counter});
                });
              });

              Scheduler.log('Test');
              return <button ref={ref}>Press me</button>;
            }

            const root = ReactDOMClient.createRoot(container);
            root.render(<Test counter={0} />);

            await waitForAll(['Test']);

            // Click the button
            dispatchClickEvent(ref.current);
            expect(log).toEqual([{counter: 0}]);

            // Clear log
            log.length = 0;

            // Increase counter
            React.startTransition(() => {
              root.render(<Test counter={1} />);
            });
            // Yield before committing
            await waitFor(['Test']);

            // Click the button again
            dispatchClickEvent(ref.current);
            expect(log).toEqual([{counter: 0}]);

            // Clear log
            log.length = 0;

            // Commit
            await waitForAll([]);
            dispatchClickEvent(ref.current);
            expect(log).toEqual([{counter: 1}]);
          });

          // @gate www
          it('should correctly work for a basic "click" window listener', async () => {
            const log = [];
            const clickEvent = jest.fn(event => {
              log.push({
                eventPhase: event.eventPhase,
                type: event.type,
                currentTarget: event.currentTarget,
                target: event.target,
              });
            });
            const setClick1 = ReactDOM.unstable_createEventHandle('click');

            function Test() {
              React.useEffect(() => {
                return setClick1(window, clickEvent);
              });

              return <button>Click anything!</button>;
            }
            const root = ReactDOMClient.createRoot(container);
            await act(() => {
              root.render(<Test />);
            });

            expect(container.innerHTML).toBe(
              '<button>Click anything!</button>',
            );

            // Clicking outside the button should trigger the event callback
            dispatchClickEvent(document.body);
            expect(log[0]).toEqual({
              eventPhase: 3,
              type: 'click',
              currentTarget: window,
              target: document.body,
            });

            // Unmounting the container and clicking should not work

            await act(() => {
              root.render(null);
            });

            dispatchClickEvent(document.body);
            expect(clickEvent).toBeCalledTimes(1);

            // Re-rendering and clicking the body should work again
            await act(() => {
              root.render(<Test />);
            });

            dispatchClickEvent(document.body);
            expect(clickEvent).toBeCalledTimes(2);
          });

          // @gate www
          it('handle propagation of click events on the window', async () => {
            const buttonRef = React.createRef();
            const divRef = React.createRef();
            const log = [];
            const onClick = jest.fn(e => log.push(['bubble', e.currentTarget]));
            const onClickCapture = jest.fn(e =>
              log.push(['capture', e.currentTarget]),
            );
            const setClick = ReactDOM.unstable_createEventHandle('click');
            const setClickCapture = ReactDOM.unstable_createEventHandle(
              'click',
              {
                capture: true,
              },
            );

            function Test() {
              React.useEffect(() => {
                const clearClick1 = setClick(window, onClick);
                const clearClickCapture1 = setClickCapture(
                  window,
                  onClickCapture,
                );
                const clearClick2 = setClick(buttonRef.current, onClick);
                const clearClickCapture2 = setClickCapture(
                  buttonRef.current,
                  onClickCapture,
                );
                const clearClick3 = setClick(divRef.current, onClick);
                const clearClickCapture3 = setClickCapture(
                  divRef.current,
                  onClickCapture,
                );

                return () => {
                  clearClick1();
                  clearClickCapture1();
                  clearClick2();
                  clearClickCapture2();
                  clearClick3();
                  clearClickCapture3();
                };
              });

              return (
                <button ref={buttonRef}>
                  <div ref={divRef}>Click me!</div>
                </button>
              );
            }

            const root = ReactDOMClient.createRoot(container);
            await act(() => {
              root.render(<Test />);
            });

            const buttonElement = buttonRef.current;
            dispatchClickEvent(buttonElement);
            expect(onClick).toHaveBeenCalledTimes(2);
            expect(onClickCapture).toHaveBeenCalledTimes(2);
            expect(log[0]).toEqual(['capture', window]);
            expect(log[1]).toEqual(['capture', buttonElement]);
            expect(log[2]).toEqual(['bubble', buttonElement]);
            expect(log[3]).toEqual(['bubble', window]);

            log.length = 0;
            onClick.mockClear();
            onClickCapture.mockClear();

            const divElement = divRef.current;
            dispatchClickEvent(divElement);
            expect(onClick).toHaveBeenCalledTimes(3);
            expect(onClickCapture).toHaveBeenCalledTimes(3);
            expect(log[0]).toEqual(['capture', window]);
            expect(log[1]).toEqual(['capture', buttonElement]);
            expect(log[2]).toEqual(['capture', divElement]);
            expect(log[3]).toEqual(['bubble', divElement]);
            expect(log[4]).toEqual(['bubble', buttonElement]);
            expect(log[5]).toEqual(['bubble', window]);
          });

          // @gate www
          it('should correctly handle stopPropagation for mixed listeners', async () => {
            const buttonRef = React.createRef();
            const rootListener1 = jest.fn(e => e.stopPropagation());
            const rootListener2 = jest.fn();
            const targetListener1 = jest.fn();
            const targetListener2 = jest.fn();
            const setClick1 = ReactDOM.unstable_createEventHandle('click', {
              capture: true,
            });
            const setClick2 = ReactDOM.unstable_createEventHandle('click', {
              capture: true,
            });
            const setClick3 = ReactDOM.unstable_createEventHandle('click');
            const setClick4 = ReactDOM.unstable_createEventHandle('click');

            function Test() {
              React.useEffect(() => {
                const clearClick1 = setClick1(window, rootListener1);
                const clearClick2 = setClick2(
                  buttonRef.current,
                  targetListener1,
                );
                const clearClick3 = setClick3(window, rootListener2);
                const clearClick4 = setClick4(
                  buttonRef.current,
                  targetListener2,
                );

                return () => {
                  clearClick1();
                  clearClick2();
                  clearClick3();
                  clearClick4();
                };
              });

              return <button ref={buttonRef}>Click me!</button>;
            }

            const root = ReactDOMClient.createRoot(container);
            await act(() => {
              root.render(<Test />);
            });

            const buttonElement = buttonRef.current;
            dispatchClickEvent(buttonElement);
            expect(rootListener1).toHaveBeenCalledTimes(1);
            expect(targetListener1).toHaveBeenCalledTimes(0);
            expect(targetListener2).toHaveBeenCalledTimes(0);
            expect(rootListener2).toHaveBeenCalledTimes(0);
          });

          // @gate www
          it('should correctly handle stopPropagation for delegated listeners', async () => {
            const buttonRef = React.createRef();
            const rootListener1 = jest.fn(e => e.stopPropagation());
            const rootListener2 = jest.fn();
            const rootListener3 = jest.fn(e => e.stopPropagation());
            const rootListener4 = jest.fn();
            const setClick1 = ReactDOM.unstable_createEventHandle('click', {
              capture: true,
            });
            const setClick2 = ReactDOM.unstable_createEventHandle('click', {
              capture: true,
            });
            const setClick3 = ReactDOM.unstable_createEventHandle('click');
            const setClick4 = ReactDOM.unstable_createEventHandle('click');

            function Test() {
              React.useEffect(() => {
                const clearClick1 = setClick1(window, rootListener1);
                const clearClick2 = setClick2(window, rootListener2);
                const clearClick3 = setClick3(window, rootListener3);
                const clearClick4 = setClick4(window, rootListener4);

                return () => {
                  clearClick1();
                  clearClick2();
                  clearClick3();
                  clearClick4();
                };
              });

              return <button ref={buttonRef}>Click me!</button>;
            }

            const root = ReactDOMClient.createRoot(container);
            await act(() => {
              root.render(<Test />);
            });

            const buttonElement = buttonRef.current;
            dispatchClickEvent(buttonElement);
            expect(rootListener1).toHaveBeenCalledTimes(1);
            expect(rootListener2).toHaveBeenCalledTimes(1);
            expect(rootListener3).toHaveBeenCalledTimes(0);
            expect(rootListener4).toHaveBeenCalledTimes(0);
          });

          // @gate www
          it('handle propagation of click events on the window and document', async () => {
            const buttonRef = React.createRef();
            const divRef = React.createRef();
            const log = [];
            const onClick = jest.fn(e => log.push(['bubble', e.currentTarget]));
            const onClickCapture = jest.fn(e =>
              log.push(['capture', e.currentTarget]),
            );
            const setClick = ReactDOM.unstable_createEventHandle('click');
            const setClickCapture = ReactDOM.unstable_createEventHandle(
              'click',
              {
                capture: true,
              },
            );

            function Test() {
              React.useEffect(() => {
                const clearClick1 = setClick(window, onClick);
                const clearClickCapture1 = setClickCapture(
                  window,
                  onClickCapture,
                );
                const clearClick2 = setClick(document, onClick);
                const clearClickCapture2 = setClickCapture(
                  document,
                  onClickCapture,
                );
                const clearClick3 = setClick(buttonRef.current, onClick);
                const clearClickCapture3 = setClickCapture(
                  buttonRef.current,
                  onClickCapture,
                );
                const clearClick4 = setClick(divRef.current, onClick);
                const clearClickCapture4 = setClickCapture(
                  divRef.current,
                  onClickCapture,
                );

                return () => {
                  clearClick1();
                  clearClickCapture1();
                  clearClick2();
                  clearClickCapture2();
                  clearClick3();
                  clearClickCapture3();
                  clearClick4();
                  clearClickCapture4();
                };
              });

              return (
                <button ref={buttonRef}>
                  <div ref={divRef}>Click me!</div>
                </button>
              );
            }

            const root = ReactDOMClient.createRoot(container);
            await act(() => {
              root.render(<Test />);
            });

            const buttonElement = buttonRef.current;
            dispatchClickEvent(buttonElement);
            expect(onClick).toHaveBeenCalledTimes(3);
            expect(onClickCapture).toHaveBeenCalledTimes(3);

            if (enableLegacyFBSupport) {
              expect(log[0]).toEqual(['capture', window]);
              expect(log[1]).toEqual(['capture', document]);
              expect(log[2]).toEqual(['capture', buttonElement]);
              expect(log[3]).toEqual(['bubble', document]);
              expect(log[4]).toEqual(['bubble', buttonElement]);
              expect(log[5]).toEqual(['bubble', window]);
            } else {
              expect(log[0]).toEqual(['capture', window]);
              expect(log[1]).toEqual(['capture', document]);
              expect(log[2]).toEqual(['capture', buttonElement]);
              expect(log[3]).toEqual(['bubble', buttonElement]);
              expect(log[4]).toEqual(['bubble', document]);
              expect(log[5]).toEqual(['bubble', window]);
            }

            log.length = 0;
            onClick.mockClear();
            onClickCapture.mockClear();

            const divElement = divRef.current;
            dispatchClickEvent(divElement);
            expect(onClick).toHaveBeenCalledTimes(4);
            expect(onClickCapture).toHaveBeenCalledTimes(4);

            if (enableLegacyFBSupport) {
              expect(log[0]).toEqual(['capture', window]);
              expect(log[1]).toEqual(['capture', document]);
              expect(log[2]).toEqual(['capture', buttonElement]);
              expect(log[3]).toEqual(['capture', divElement]);
              expect(log[4]).toEqual(['bubble', document]);
              expect(log[5]).toEqual(['bubble', divElement]);
              expect(log[6]).toEqual(['bubble', buttonElement]);
              expect(log[7]).toEqual(['bubble', window]);
            } else {
              expect(log[0]).toEqual(['capture', window]);
              expect(log[1]).toEqual(['capture', document]);
              expect(log[2]).toEqual(['capture', buttonElement]);
              expect(log[3]).toEqual(['capture', divElement]);
              expect(log[4]).toEqual(['bubble', divElement]);
              expect(log[5]).toEqual(['bubble', buttonElement]);
              expect(log[6]).toEqual(['bubble', document]);
              expect(log[7]).toEqual(['bubble', window]);
            }
          });

          // @gate www
          it('does not support custom user events', () => {
            // With eager listeners, supporting custom events via this API doesn't make sense
            // because we can't know a full list of them ahead of time. Let's check we throw
            // since otherwise we'd end up with inconsistent behavior, like no portal bubbling.
            expect(() => {
              ReactDOM.unstable_createEventHandle('custom-event');
            }).toThrow(
              'Cannot call unstable_createEventHandle with "custom-event", as it is not an event known to React.',
            );
          });

          // @gate www
          it('beforeblur and afterblur are called after a focused element is unmounted', async () => {
            const log = [];
            // We have to persist here because we want to read relatedTarget later.
            const onAfterBlur = jest.fn(e => {
              e.persist();
              log.push(e.type);
            });
            const onBeforeBlur = jest.fn(e => log.push(e.type));
            const innerRef = React.createRef();
            const innerRef2 = React.createRef();
            const setAfterBlurHandle =
              ReactDOM.unstable_createEventHandle('afterblur');
            const setBeforeBlurHandle =
              ReactDOM.unstable_createEventHandle('beforeblur');

            const Component = ({show}) => {
              const ref = React.useRef(null);

              React.useEffect(() => {
                const clear1 = setAfterBlurHandle(document, onAfterBlur);
                const clear2 = setBeforeBlurHandle(ref.current, onBeforeBlur);

                return () => {
                  clear1();
                  clear2();
                };
              });

              return (
                <div ref={ref}>
                  {show && <input ref={innerRef} />}
                  <div ref={innerRef2} />
                </div>
              );
            };

            const root = ReactDOMClient.createRoot(container);
            await act(() => {
              root.render(<Component show={true} />);
            });

            const inner = innerRef.current;
            const target = createEventTarget(inner);
            target.focus();
            expect(onBeforeBlur).toHaveBeenCalledTimes(0);
            expect(onAfterBlur).toHaveBeenCalledTimes(0);

            await act(() => {
              root.render(<Component show={false} />);
            });

            expect(onBeforeBlur).toHaveBeenCalledTimes(1);
            expect(onAfterBlur).toHaveBeenCalledTimes(1);
            expect(onAfterBlur).toHaveBeenCalledWith(
              expect.objectContaining({relatedTarget: inner}),
            );
            expect(log).toEqual(['beforeblur', 'afterblur']);
          });

          // @gate www
          it('beforeblur and afterblur are called after a nested focused element is unmounted', async () => {
            const log = [];
            // We have to persist here because we want to read relatedTarget later.
            const onAfterBlur = jest.fn(e => {
              e.persist();
              log.push(e.type);
            });
            const onBeforeBlur = jest.fn(e => log.push(e.type));
            const innerRef = React.createRef();
            const innerRef2 = React.createRef();
            const setAfterBlurHandle =
              ReactDOM.unstable_createEventHandle('afterblur');
            const setBeforeBlurHandle =
              ReactDOM.unstable_createEventHandle('beforeblur');

            const Component = ({show}) => {
              const ref = React.useRef(null);

              React.useEffect(() => {
                const clear1 = setAfterBlurHandle(document, onAfterBlur);
                const clear2 = setBeforeBlurHandle(ref.current, onBeforeBlur);

                return () => {
                  clear1();
                  clear2();
                };
              });

              return (
                <div ref={ref}>
                  {show && (
                    <div>
                      <input ref={innerRef} />
                    </div>
                  )}
                  <div ref={innerRef2} />
                </div>
              );
            };

            const root = ReactDOMClient.createRoot(container);
            await act(() => {
              root.render(<Component show={true} />);
            });

            const inner = innerRef.current;
            const target = createEventTarget(inner);
            target.focus();
            expect(onBeforeBlur).toHaveBeenCalledTimes(0);
            expect(onAfterBlur).toHaveBeenCalledTimes(0);

            await act(() => {
              root.render(<Component show={false} />);
            });

            expect(onBeforeBlur).toHaveBeenCalledTimes(1);
            expect(onAfterBlur).toHaveBeenCalledTimes(1);
            expect(onAfterBlur).toHaveBeenCalledWith(
              expect.objectContaining({relatedTarget: inner}),
            );
            expect(log).toEqual(['beforeblur', 'afterblur']);
          });

          // @gate www
          it('beforeblur should skip handlers from a deleted subtree after the focused element is unmounted', async () => {
            const onBeforeBlur = jest.fn();
            const innerRef = React.createRef();
            const innerRef2 = React.createRef();
            const setBeforeBlurHandle =
              ReactDOM.unstable_createEventHandle('beforeblur');
            const ref2 = React.createRef();

            const Component = ({show}) => {
              const ref = React.useRef(null);

              React.useEffect(() => {
                const clear1 = setBeforeBlurHandle(ref.current, onBeforeBlur);
                let clear2;
                if (ref2.current) {
                  clear2 = setBeforeBlurHandle(ref2.current, onBeforeBlur);
                }

                return () => {
                  clear1();
                  if (clear2) {
                    clear2();
                  }
                };
              });

              return (
                <div ref={ref}>
                  {show && (
                    <div ref={ref2}>
                      <input ref={innerRef} />
                    </div>
                  )}
                  <div ref={innerRef2} />
                </div>
              );
            };

            const root = ReactDOMClient.createRoot(container);
            await act(() => {
              root.render(<Component show={true} />);
            });

            const inner = innerRef.current;
            const target = createEventTarget(inner);
            target.focus();
            expect(onBeforeBlur).toHaveBeenCalledTimes(0);

            await act(() => {
              root.render(<Component show={false} />);
            });

            expect(onBeforeBlur).toHaveBeenCalledTimes(1);
          });

          // @gate www
          it('beforeblur and afterblur are called after a focused element is suspended', async () => {
            const log = [];
            // We have to persist here because we want to read relatedTarget later.
            const onAfterBlur = jest.fn(e => {
              e.persist();
              log.push(e.type);
            });
            const onBeforeBlur = jest.fn(e => log.push(e.type));
            const innerRef = React.createRef();
            const Suspense = React.Suspense;
            let suspend = false;
            let resolve;
            const promise = new Promise(
              resolvePromise => (resolve = resolvePromise),
            );
            const setAfterBlurHandle =
              ReactDOM.unstable_createEventHandle('afterblur');
            const setBeforeBlurHandle =
              ReactDOM.unstable_createEventHandle('beforeblur');

            function Child() {
              if (suspend) {
                throw promise;
              } else {
                return <input ref={innerRef} />;
              }
            }

            const Component = () => {
              const ref = React.useRef(null);

              React.useEffect(() => {
                const clear1 = setAfterBlurHandle(document, onAfterBlur);
                const clear2 = setBeforeBlurHandle(ref.current, onBeforeBlur);

                return () => {
                  clear1();
                  clear2();
                };
              });

              return (
                <div ref={ref}>
                  <Suspense fallback="Loading...">
                    <Child />
                  </Suspense>
                </div>
              );
            };

            const container2 = document.createElement('div');
            document.body.appendChild(container2);

            const root = ReactDOMClient.createRoot(container2);

            await act(() => {
              root.render(<Component />);
            });
            jest.runAllTimers();

            const inner = innerRef.current;
            const target = createEventTarget(inner);
            target.focus();
            expect(onBeforeBlur).toHaveBeenCalledTimes(0);
            expect(onAfterBlur).toHaveBeenCalledTimes(0);

            suspend = true;
            await act(() => {
              root.render(<Component />);
            });
            jest.runAllTimers();

            expect(onBeforeBlur).toHaveBeenCalledTimes(1);
            expect(onAfterBlur).toHaveBeenCalledTimes(1);
            expect(onAfterBlur).toHaveBeenCalledWith(
              expect.objectContaining({relatedTarget: inner}),
            );
            resolve();
            expect(log).toEqual(['beforeblur', 'afterblur']);

            document.body.removeChild(container2);
          });

          // @gate www
          it('beforeblur should skip handlers from a deleted subtree after the focused element is suspended', async () => {
            const onBeforeBlur = jest.fn();
            const innerRef = React.createRef();
            const innerRef2 = React.createRef();
            const setBeforeBlurHandle =
              ReactDOM.unstable_createEventHandle('beforeblur');
            const ref2 = React.createRef();
            const Suspense = React.Suspense;
            let suspend = false;
            let resolve;
            const promise = new Promise(
              resolvePromise => (resolve = resolvePromise),
            );

            function Child() {
              if (suspend) {
                throw promise;
              } else {
                return <input ref={innerRef} />;
              }
            }

            const Component = () => {
              const ref = React.useRef(null);

              React.useEffect(() => {
                const clear1 = setBeforeBlurHandle(ref.current, onBeforeBlur);
                let clear2;
                if (ref2.current) {
                  clear2 = setBeforeBlurHandle(ref2.current, onBeforeBlur);
                }

                return () => {
                  clear1();
                  if (clear2) {
                    clear2();
                  }
                };
              });

              return (
                <div ref={ref}>
                  <Suspense fallback="Loading...">
                    <div ref={ref2}>
                      <Child />
                    </div>
                  </Suspense>
                  <div ref={innerRef2} />
                </div>
              );
            };

            const container2 = document.createElement('div');
            document.body.appendChild(container2);

            const root = ReactDOMClient.createRoot(container2);

            await act(() => {
              root.render(<Component />);
            });
            jest.runAllTimers();

            const inner = innerRef.current;
            const target = createEventTarget(inner);
            target.focus();
            expect(onBeforeBlur).toHaveBeenCalledTimes(0);

            suspend = true;
            await act(() => {
              root.render(<Component />);
            });
            jest.runAllTimers();

            expect(onBeforeBlur).toHaveBeenCalledTimes(1);
            resolve();

            document.body.removeChild(container2);
          });

          // @gate www
          it('regression: does not fire beforeblur/afterblur if target is already hidden', async () => {
            const Suspense = React.Suspense;
            let suspend = false;
            const fakePromise = {then() {}};
            const setBeforeBlurHandle =
              ReactDOM.unstable_createEventHandle('beforeblur');
            const innerRef = React.createRef();

            function Child() {
              if (suspend) {
                throw fakePromise;
              }
              return <input ref={innerRef} />;
            }

            const Component = () => {
              const ref = React.useRef(null);
              const [, setState] = React.useState(0);

              React.useEffect(() => {
                return setBeforeBlurHandle(ref.current, () => {
                  // In the regression case, this would trigger an update, then
                  // the resulting render would trigger another blur event,
                  // which would trigger an update again, and on and on in an
                  // infinite loop.
                  setState(n => n + 1);
                });
              }, []);

              return (
                <div ref={ref}>
                  <Suspense fallback="Loading...">
                    <Child />
                  </Suspense>
                </div>
              );
            };

            const container2 = document.createElement('div');
            document.body.appendChild(container2);

            const root = ReactDOMClient.createRoot(container2);
            await act(() => {
              root.render(<Component />);
            });

            // Focus the input node
            const inner = innerRef.current;
            const target = createEventTarget(inner);
            target.focus();

            // Suspend. This hides the input node, causing it to lose focus.
            suspend = true;
            await act(() => {
              root.render(<Component />);
            });

            document.body.removeChild(container2);
          });

          // @gate !disableCommentsAsDOMContainers
          it('handle propagation of click events between disjointed comment roots', async () => {
            const buttonRef = React.createRef();
            const divRef = React.createRef();
            const log = [];
            const setClick = ReactDOM.unstable_createEventHandle('click');
            const setClickCapture = ReactDOM.unstable_createEventHandle(
              'click',
              {capture: true},
            );
            const onClick = jest.fn(e => log.push(['bubble', e.currentTarget]));
            const onClickCapture = jest.fn(e =>
              log.push(['capture', e.currentTarget]),
            );

            function Child() {
              React.useEffect(() => {
                const click1 = setClick(divRef.current, onClick);
                const click2 = setClickCapture(divRef.current, onClickCapture);
                return () => {
                  click1();
                  click2();
                };
              });

              return <div ref={divRef}>Click me!</div>;
            }

            function Parent() {
              React.useEffect(() => {
                const click1 = setClick(buttonRef.current, onClick);
                const click2 = setClickCapture(
                  buttonRef.current,
                  onClickCapture,
                );
                return () => {
                  click1();
                  click2();
                };
              });

              return <button ref={buttonRef} />;
            }

            // We use a comment node here, then mount to it
            const disjointedNode = document.createComment(
              ' react-mount-point-unstable ',
            );
            const root = ReactDOMClient.createRoot(container);
            await act(() => {
              root.render(<Parent />);
            });
            buttonRef.current.appendChild(disjointedNode);
            const disjointedNodeRoot =
              ReactDOMClient.createRoot(disjointedNode);
            await act(() => {
              disjointedNodeRoot.render(<Child />);
            });

            const buttonElement = buttonRef.current;
            dispatchClickEvent(buttonElement);
            expect(onClick).toHaveBeenCalledTimes(1);
            expect(onClickCapture).toHaveBeenCalledTimes(1);
            expect(log[0]).toEqual(['capture', buttonElement]);
            expect(log[1]).toEqual(['bubble', buttonElement]);

            const divElement = divRef.current;
            dispatchClickEvent(divElement);
            expect(onClick).toHaveBeenCalledTimes(3);
            expect(onClickCapture).toHaveBeenCalledTimes(3);
            expect(log[2]).toEqual(['capture', buttonElement]);
            expect(log[3]).toEqual(['capture', divElement]);
            expect(log[4]).toEqual(['bubble', divElement]);
            expect(log[5]).toEqual(['bubble', buttonElement]);
          });

          // @gate www
          it('propagates known createEventHandle events through portals without inner listeners', async () => {
            const buttonRef = React.createRef();
            const divRef = React.createRef();
            const log = [];
            const onClick = jest.fn(e => log.push(['bubble', e.currentTarget]));
            const onClickCapture = jest.fn(e =>
              log.push(['capture', e.currentTarget]),
            );
            const setClick = ReactDOM.unstable_createEventHandle('click');
            const setClickCapture = ReactDOM.unstable_createEventHandle(
              'click',
              {
                capture: true,
              },
            );

            const portalElement = document.createElement('div');
            document.body.appendChild(portalElement);

            function Child() {
              return <div ref={divRef}>Click me!</div>;
            }

            function Parent() {
              React.useEffect(() => {
                const clear1 = setClick(buttonRef.current, onClick);
                const clear2 = setClickCapture(
                  buttonRef.current,
                  onClickCapture,
                );
                return () => {
                  clear1();
                  clear2();
                };
              });

              return (
                <button ref={buttonRef}>
                  {ReactDOM.createPortal(<Child />, portalElement)}
                </button>
              );
            }

            const root = ReactDOMClient.createRoot(container);
            await act(() => {
              root.render(<Parent />);
            });

            const divElement = divRef.current;
            const buttonElement = buttonRef.current;
            dispatchClickEvent(divElement);
            expect(onClick).toHaveBeenCalledTimes(1);
            expect(onClickCapture).toHaveBeenCalledTimes(1);
            expect(log[0]).toEqual(['capture', buttonElement]);
            expect(log[1]).toEqual(['bubble', buttonElement]);

            document.body.removeChild(portalElement);
          });

          describe('Compatibility with Scopes API', () => {
            beforeEach(() => {
              jest.resetModules();
              ReactFeatureFlags = require('shared/ReactFeatureFlags');
              ReactFeatureFlags.enableCreateEventHandleAPI = true;
              ReactFeatureFlags.enableScopeAPI = true;

              React = require('react');
              ReactDOM = require('react-dom');
              ReactDOMClient = require('react-dom/client');
              Scheduler = require('scheduler');
              ReactDOMServer = require('react-dom/server');
              act = require('internal-test-utils').act;
            });

            // @gate www
            it('handle propagation of click events on a scope', async () => {
              const buttonRef = React.createRef();
              const log = [];
              const onClick = jest.fn(e =>
                log.push(['bubble', e.currentTarget]),
              );
              const onClickCapture = jest.fn(e =>
                log.push(['capture', e.currentTarget]),
              );
              const TestScope = React.unstable_Scope;
              const setClick = ReactDOM.unstable_createEventHandle('click');
              const setClickCapture = ReactDOM.unstable_createEventHandle(
                'click',
                {
                  capture: true,
                },
              );

              function Test() {
                const scopeRef = React.useRef(null);

                React.useEffect(() => {
                  const clear1 = setClick(scopeRef.current, onClick);
                  const clear2 = setClickCapture(
                    scopeRef.current,
                    onClickCapture,
                  );

                  return () => {
                    clear1();
                    clear2();
                  };
                });

                return (
                  <TestScope ref={scopeRef}>
                    <button ref={buttonRef} />
                  </TestScope>
                );
              }

              const root = ReactDOMClient.createRoot(container);
              await act(() => {
                root.render(<Test />);
              });

              const buttonElement = buttonRef.current;
              dispatchClickEvent(buttonElement);

              expect(onClick).toHaveBeenCalledTimes(1);
              expect(onClickCapture).toHaveBeenCalledTimes(1);
              expect(log).toEqual([
                ['capture', buttonElement],
                ['bubble', buttonElement],
              ]);
            });

            // @gate www
            it('handle mixed propagation of click events on a scope', async () => {
              const buttonRef = React.createRef();
              const divRef = React.createRef();
              const log = [];
              const onClick = jest.fn(e =>
                log.push(['bubble', e.currentTarget]),
              );
              const onClickCapture = jest.fn(e =>
                log.push(['capture', e.currentTarget]),
              );
              const TestScope = React.unstable_Scope;
              const setClick = ReactDOM.unstable_createEventHandle('click');
              const setClickCapture = ReactDOM.unstable_createEventHandle(
                'click',
                {
                  capture: true,
                },
              );

              function Test() {
                const scopeRef = React.useRef(null);

                React.useEffect(() => {
                  const clear1 = setClick(scopeRef.current, onClick);
                  const clear2 = setClickCapture(
                    scopeRef.current,
                    onClickCapture,
                  );
                  const clear3 = setClick(buttonRef.current, onClick);
                  const clear4 = setClickCapture(
                    buttonRef.current,
                    onClickCapture,
                  );

                  return () => {
                    clear1();
                    clear2();
                    clear3();
                    clear4();
                  };
                });

                return (
                  <TestScope ref={scopeRef}>
                    <button ref={buttonRef}>
                      <div
                        ref={divRef}
                        onClick={onClick}
                        onClickCapture={onClickCapture}>
                        Click me!
                      </div>
                    </button>
                  </TestScope>
                );
              }

              const root = ReactDOMClient.createRoot(container);
              await act(() => {
                root.render(<Test />);
              });

              const buttonElement = buttonRef.current;
              dispatchClickEvent(buttonElement);

              expect(onClick).toHaveBeenCalledTimes(2);
              expect(onClickCapture).toHaveBeenCalledTimes(2);
              expect(log).toEqual([
                ['capture', buttonElement],
                ['capture', buttonElement],
                ['bubble', buttonElement],
                ['bubble', buttonElement],
              ]);

              log.length = 0;
              onClick.mockClear();
              onClickCapture.mockClear();

              const divElement = divRef.current;
              dispatchClickEvent(divElement);

              expect(onClick).toHaveBeenCalledTimes(3);
              expect(onClickCapture).toHaveBeenCalledTimes(3);
              expect(log).toEqual([
                ['capture', buttonElement],
                ['capture', buttonElement],
                ['capture', divElement],
                ['bubble', divElement],
                ['bubble', buttonElement],
                ['bubble', buttonElement],
              ]);
            });

            // @gate www
            it('should not handle the target being a dangling text node within a scope', async () => {
              const clickEvent = jest.fn();
              const buttonRef = React.createRef();
              const TestScope = React.unstable_Scope;
              const setClick = ReactDOM.unstable_createEventHandle('click');

              function Test() {
                const scopeRef = React.useRef(null);

                React.useEffect(() => {
                  return setClick(scopeRef.current, clickEvent);
                });

                return (
                  <button ref={buttonRef}>
                    <TestScope ref={scopeRef}>Click me!</TestScope>
                  </button>
                );
              }

              const root = ReactDOMClient.createRoot(container);
              await act(() => {
                root.render(<Test />);
              });

              const textNode = buttonRef.current.firstChild;
              dispatchClickEvent(textNode);
              // This should not work, as the target instance will be the
              // <button>, which is actually outside the scope.
              expect(clickEvent).toBeCalledTimes(0);
            });

            // @gate www
            it('handle stopPropagation (inner) correctly between scopes', async () => {
              const buttonRef = React.createRef();
              const outerOnClick = jest.fn();
              const innerOnClick = jest.fn(e => e.stopPropagation());
              const TestScope = React.unstable_Scope;
              const TestScope2 = React.unstable_Scope;
              const setClick = ReactDOM.unstable_createEventHandle('click');

              function Test() {
                const scopeRef = React.useRef(null);
                const scope2Ref = React.useRef(null);

                React.useEffect(() => {
                  const clear1 = setClick(scopeRef.current, outerOnClick);
                  const clear2 = setClick(scope2Ref.current, innerOnClick);

                  return () => {
                    clear1();
                    clear2();
                  };
                });

                return (
                  <TestScope ref={scopeRef}>
                    <TestScope2 ref={scope2Ref}>
                      <button ref={buttonRef} />
                    </TestScope2>
                  </TestScope>
                );
              }

              const root = ReactDOMClient.createRoot(container);
              await act(() => {
                root.render(<Test />);
              });

              const buttonElement = buttonRef.current;
              dispatchClickEvent(buttonElement);

              expect(innerOnClick).toHaveBeenCalledTimes(1);
              expect(outerOnClick).toHaveBeenCalledTimes(0);
            });

            // @gate www
            it('handle stopPropagation (outer) correctly between scopes', async () => {
              const buttonRef = React.createRef();
              const outerOnClick = jest.fn(e => e.stopPropagation());
              const innerOnClick = jest.fn();
              const TestScope = React.unstable_Scope;
              const TestScope2 = React.unstable_Scope;
              const setClick = ReactDOM.unstable_createEventHandle('click');

              function Test() {
                const scopeRef = React.useRef(null);
                const scope2Ref = React.useRef(null);

                React.useEffect(() => {
                  const clear1 = setClick(scopeRef.current, outerOnClick);
                  const clear2 = setClick(scope2Ref.current, innerOnClick);

                  return () => {
                    clear1();
                    clear2();
                  };
                });

                return (
                  <TestScope ref={scopeRef}>
                    <TestScope2 ref={scope2Ref}>
                      <button ref={buttonRef} />
                    </TestScope2>
                  </TestScope>
                );
              }

              const root = ReactDOMClient.createRoot(container);
              await act(() => {
                root.render(<Test />);
              });

              const buttonElement = buttonRef.current;
              dispatchClickEvent(buttonElement);

              expect(innerOnClick).toHaveBeenCalledTimes(1);
              expect(outerOnClick).toHaveBeenCalledTimes(1);
            });

            // @gate www
            it('handle stopPropagation (inner and outer) correctly between scopes', async () => {
              const buttonRef = React.createRef();
              const onClick = jest.fn(e => e.stopPropagation());
              const TestScope = React.unstable_Scope;
              const TestScope2 = React.unstable_Scope;
              const setClick = ReactDOM.unstable_createEventHandle('click');

              function Test() {
                const scopeRef = React.useRef(null);
                const scope2Ref = React.useRef(null);

                React.useEffect(() => {
                  const clear1 = setClick(scopeRef.current, onClick);
                  const clear2 = setClick(scope2Ref.current, onClick);

                  return () => {
                    clear1();
                    clear2();
                  };
                });

                return (
                  <TestScope ref={scopeRef}>
                    <TestScope2 ref={scope2Ref}>
                      <button ref={buttonRef} />
                    </TestScope2>
                  </TestScope>
                );
              }

              const root = ReactDOMClient.createRoot(container);
              await act(() => {
                root.render(<Test />);
              });

              const buttonElement = buttonRef.current;
              dispatchClickEvent(buttonElement);

              expect(onClick).toHaveBeenCalledTimes(1);
            });

            // @gate www
            it('should be able to register handlers for events affected by the intervention', async () => {
              const rootContainer = document.createElement('div');
              container.appendChild(rootContainer);

              const allEvents = [];
              const defaultPreventedEvents = [];
              const handler = e => {
                allEvents.push(e.type);
                if (e.defaultPrevented) defaultPreventedEvents.push(e.type);
              };

              container.addEventListener('touchstart', handler);
              container.addEventListener('touchmove', handler);
              container.addEventListener('wheel', handler);

              const ref = React.createRef();
              const setTouchStart =
                ReactDOM.unstable_createEventHandle('touchstart');
              const setTouchMove =
                ReactDOM.unstable_createEventHandle('touchmove');
              const setWheel = ReactDOM.unstable_createEventHandle('wheel');

              function Component() {
                React.useEffect(() => {
                  const clearTouchStart = setTouchStart(ref.current, e =>
                    e.preventDefault(),
                  );
                  const clearTouchMove = setTouchMove(ref.current, e =>
                    e.preventDefault(),
                  );
                  const clearWheel = setWheel(ref.current, e =>
                    e.preventDefault(),
                  );
                  return () => {
                    clearTouchStart();
                    clearTouchMove();
                    clearWheel();
                  };
                });
                return <div ref={ref}>test</div>;
              }

              const root = ReactDOMClient.createRoot(rootContainer);
              await act(() => {
                root.render(<Component />);
              });

              dispatchEvent(ref.current, 'touchstart');
              dispatchEvent(ref.current, 'touchmove');
              dispatchEvent(ref.current, 'wheel');

              expect(allEvents).toEqual(['touchstart', 'touchmove', 'wheel']);
              // These events are passive by default, so we can't preventDefault.
              expect(defaultPreventedEvents).toEqual([]);
            });
          });
        });
      },
    );
  }
```

### Buggy: 1 (Commit: 32fc489632377d214db55bfa4e2c48486a7d7ce2)
**Repo**: axios
```javascript
validateStatus(status) {
        return status !== 500;
      }
```

### Buggy: 0 (Commit: 520dd77a35922fb537e2dbfb3c839d047acbdd68)
**Repo**: eslint
```javascript
forEachName(callback) {
		this.#functions.forEach((funcs, name) => {
			callback(name);
		});
	}
```

### Buggy: 1 (Commit: 430bd41ab24028d69aae1166762d771fc71339f1)
**Repo**: webpack
```javascript
function se(t,{instancePath:n="",parentData:o,parentDataProperty:s,rootData:i=t}={}){let a=null,l=0;if(0===l){if(!t||"object"!=typeof t||Array.isArray(t))return se.errors=[{params:{type:"object"}}],!1;{const o=l;for(const e in t)if(!r.call(re.properties,e))return se.errors=[{params:{additionalProperty:e}}],!1;if(o===l){if(void 0!==t.alias){let e=t.alias;const n=l,r=l;let o=!1;const s=l;if(l===s)if(Array.isArray(e)){const t=e.length;for(let n=0;n<t;n++){let t=e[n];const r=l;if(l===r)if(t&&"object"==typeof t&&!Array.isArray(t)){let e;if(void 0===t.alias&&(e="alias")||void 0===t.name&&(e="name")){const t={params:{missingProperty:e}};null===a?a=[t]:a.push(t),l++}else{const e=l;for(const e in t)if("alias"!==e&&"name"!==e&&"onlyModule"!==e){const t={params:{additionalProperty:e}};null===a?a=[t]:a.push(t),l++;break}if(e===l){if(void 0!==t.alias){let e=t.alias;const n=l,r=l;let o=!1;const s=l;if(l===s)if(Array.isArray(e)){const t=e.length;for(let n=0;n<t;n++){let t=e[n];const r=l;if(l===r)if("string"==typeof t){if(t.length<1){const e={params:{}};null===a?a=[e]:a.push(e),l++}}else{const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}if(r!==l)break}}else{const e={params:{type:"array"}};null===a?a=[e]:a.push(e),l++}var p=s===l;if(o=o||p,!o){const t=l;if(!1!==e){const e={params:{}};null===a?a=[e]:a.push(e),l++}if(p=t===l,o=o||p,!o){const t=l;if(l===t)if("string"==typeof e){if(e.length<1){const e={params:{}};null===a?a=[e]:a.push(e),l++}}else{const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}p=t===l,o=o||p}}if(o)l=r,null!==a&&(r?a.length=r:a=null);else{const e={params:{}};null===a?a=[e]:a.push(e),l++}var f=n===l}else f=!0;if(f){if(void 0!==t.name){const e=l;if("string"!=typeof t.name){const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}f=e===l}else f=!0;if(f)if(void 0!==t.onlyModule){const e=l;if("boolean"!=typeof t.onlyModule){const e={params:{type:"boolean"}};null===a?a=[e]:a.push(e),l++}f=e===l}else f=!0}}}}else{const e={params:{type:"object"}};null===a?a=[e]:a.push(e),l++}if(r!==l)break}}else{const e={params:{type:"array"}};null===a?a=[e]:a.push(e),l++}var u=s===l;if(o=o||u,!o){const t=l;if(l===t)if(e&&"object"==typeof e&&!Array.isArray(e))for(const t in e){let n=e[t];const r=l,o=l;let s=!1;const i=l;if(l===i)if(Array.isArray(n)){const e=n.length;for(let t=0;t<e;t++){let e=n[t];const r=l;if(l===r)if("string"==typeof e){if(e.length<1){const e={params:{}};null===a?a=[e]:a.push(e),l++}}else{const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}if(r!==l)break}}else{const e={params:{type:"array"}};null===a?a=[e]:a.push(e),l++}var c=i===l;if(s=s||c,!s){const e=l;if(!1!==n){const e={params:{}};null===a?a=[e]:a.push(e),l++}if(c=e===l,s=s||c,!s){const e=l;if(l===e)if("string"==typeof n){if(n.length<1){const e={params:{}};null===a?a=[e]:a.push(e),l++}}else{const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}c=e===l,s=s||c}}if(s)l=o,null!==a&&(o?a.length=o:a=null);else{const e={params:{}};null===a?a=[e]:a.push(e),l++}if(r!==l)break}else{const e={params:{type:"object"}};null===a?a=[e]:a.push(e),l++}u=t===l,o=o||u}if(!o){const e={params:{}};return null===a?a=[e]:a.push(e),l++,se.errors=a,!1}l=r,null!==a&&(r?a.length=r:a=null);var y=n===l}else y=!0;if(y){if(void 0!==t.aliasFields){let e=t.aliasFields;const n=l;if(l===n){if(!Array.isArray(e))return se.errors=[{params:{type:"array"}}],!1;{const t=e.length;for(let n=0;n<t;n++){let t=e[n];const r=l,o=l;let s=!1;const i=l;if(l===i)if(Array.isArray(t)){const e=t.length;for(let n=0;n<e;n++){let e=t[n];const r=l;if(l===r)if("string"==typeof e){if(e.length<1){const e={params:{}};null===a?a=[e]:a.push(e),l++}}else{const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}if(r!==l)break}}else{const e={params:{type:"array"}};null===a?a=[e]:a.push(e),l++}var m=i===l;if(s=s||m,!s){const e=l;if(l===e)if("string"==typeof t){if(t.length<1){const e={params:{}};null===a?a=[e]:a.push(e),l++}}else{const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}m=e===l,s=s||m}if(!s){const e={params:{}};return null===a?a=[e]:a.push(e),l++,se.errors=a,!1}if(l=o,null!==a&&(o?a.length=o:a=null),r!==l)break}}}y=n===l}else y=!0;if(y){if(void 0!==t.byDependency){let e=t.byDependency;const r=l;if(l===r){if(!e||"object"!=typeof e||Array.isArray(e))return se.errors=[{params:{type:"object"}}],!1;for(const t in e){const r=l,o=l;let s=!1,p=null;const f=l;if(oe.validate(e[t],{instancePath:n+"/byDependency/"+t.replace(/~/g,"~0").replace(/\//g,"~1"),parentData:e,parentDataProperty:t,rootData:i})||(a=null===a?oe.validate.errors:a.concat(oe.validate.errors),l=a.length),f===l&&(s=!0,p=0),!s){const e={params:{passingSchemas:p}};return null===a?a=[e]:a.push(e),l++,se.errors=a,!1}if(l=o,null!==a&&(o?a.length=o:a=null),r!==l)break}}y=r===l}else y=!0;if(y){if(void 0!==t.cache){const e=l;if("boolean"!=typeof t.cache)return se.errors=[{params:{type:"boolean"}}],!1;y=e===l}else y=!0;if(y){if(void 0!==t.cachePredicate){const e=l;if(!(t.cachePredicate instanceof Function))return se.errors=[{params:{}}],!1;y=e===l}else y=!0;if(y){if(void 0!==t.cacheWithContext){const e=l;if("boolean"!=typeof t.cacheWithContext)return se.errors=[{params:{type:"boolean"}}],!1;y=e===l}else y=!0;if(y){if(void 0!==t.conditionNames){let e=t.conditionNames;const n=l;if(l===n){if(!Array.isArray(e))return se.errors=[{params:{type:"array"}}],!1;{const t=e.length;for(let n=0;n<t;n++){const t=l;if("string"!=typeof e[n])return se.errors=[{params:{type:"string"}}],!1;if(t!==l)break}}}y=n===l}else y=!0;if(y){if(void 0!==t.descriptionFiles){let e=t.descriptionFiles;const n=l;if(l===n){if(!Array.isArray(e))return se.errors=[{params:{type:"array"}}],!1;{const t=e.length;for(let n=0;n<t;n++){let t=e[n];const r=l;if(l===r){if("string"!=typeof t)return se.errors=[{params:{type:"string"}}],!1;if(t.length<1)return se.errors=[{params:{}}],!1}if(r!==l)break}}}y=n===l}else y=!0;if(y){if(void 0!==t.enforceExtension){const e=l;if("boolean"!=typeof t.enforceExtension)return se.errors=[{params:{type:"boolean"}}],!1;y=e===l}else y=!0;if(y){if(void 0!==t.exportsFields){let e=t.exportsFields;const n=l;if(l===n){if(!Array.isArray(e))return se.errors=[{params:{type:"array"}}],!1;{const t=e.length;for(let n=0;n<t;n++){const t=l;if("string"!=typeof e[n])return se.errors=[{params:{type:"string"}}],!1;if(t!==l)break}}}y=n===l}else y=!0;if(y){if(void 0!==t.extensionAlias){let e=t.extensionAlias;const n=l;if(l===n){if(!e||"object"!=typeof e||Array.isArray(e))return se.errors=[{params:{type:"object"}}],!1;for(const t in e){let n=e[t];const r=l,o=l;let s=!1;const i=l;if(l===i)if(Array.isArray(n)){const e=n.length;for(let t=0;t<e;t++){let e=n[t];const r=l;if(l===r)if("string"==typeof e){if(e.length<1){const e={params:{}};null===a?a=[e]:a.push(e),l++}}else{const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}if(r!==l)break}}else{const e={params:{type:"array"}};null===a?a=[e]:a.push(e),l++}var d=i===l;if(s=s||d,!s){const e=l;if(l===e)if("string"==typeof n){if(n.length<1){const e={params:{}};null===a?a=[e]:a.push(e),l++}}else{const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}d=e===l,s=s||d}if(!s){const e={params:{}};return null===a?a=[e]:a.push(e),l++,se.errors=a,!1}if(l=o,null!==a&&(o?a.length=o:a=null),r!==l)break}}y=n===l}else y=!0;if(y){if(void 0!==t.extensions){let e=t.extensions;const n=l;if(l===n){if(!Array.isArray(e))return se.errors=[{params:{type:"array"}}],!1;{const t=e.length;for(let n=0;n<t;n++){const t=l;if("string"!=typeof e[n])return se.errors=[{params:{type:"string"}}],!1;if(t!==l)break}}}y=n===l}else y=!0;if(y){if(void 0!==t.fallback){let e=t.fallback;const n=l,r=l;let o=!1,s=null;const i=l,p=l;let f=!1;const u=l;if(l===u)if(Array.isArray(e)){const t=e.length;for(let n=0;n<t;n++){let t=e[n];const r=l;if(l===r)if(t&&"object"==typeof t&&!Array.isArray(t)){let e;if(void 0===t.alias&&(e="alias")||void 0===t.name&&(e="name")){const t={params:{missingProperty:e}};null===a?a=[t]:a.push(t),l++}else{const e=l;for(const e in t)if("alias"!==e&&"name"!==e&&"onlyModule"!==e){const t={params:{additionalProperty:e}};null===a?a=[t]:a.push(t),l++;break}if(e===l){if(void 0!==t.alias){let e=t.alias;const n=l,r=l;let o=!1;const s=l;if(l===s)if(Array.isArray(e)){const t=e.length;for(let n=0;n<t;n++){let t=e[n];const r=l;if(l===r)if("string"==typeof t){if(t.length<1){const e={params:{}};null===a?a=[e]:a.push(e),l++}}else{const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}if(r!==l)break}}else{const e={params:{type:"array"}};null===a?a=[e]:a.push(e),l++}var h=s===l;if(o=o||h,!o){const t=l;if(!1!==e){const e={params:{}};null===a?a=[e]:a.push(e),l++}if(h=t===l,o=o||h,!o){const t=l;if(l===t)if("string"==typeof e){if(e.length<1){const e={params:{}};null===a?a=[e]:a.push(e),l++}}else{const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}h=t===l,o=o||h}}if(o)l=r,null!==a&&(r?a.length=r:a=null);else{const e={params:{}};null===a?a=[e]:a.push(e),l++}var b=n===l}else b=!0;if(b){if(void 0!==t.name){const e=l;if("string"!=typeof t.name){const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}b=e===l}else b=!0;if(b)if(void 0!==t.onlyModule){const e=l;if("boolean"!=typeof t.onlyModule){const e={params:{type:"boolean"}};null===a?a=[e]:a.push(e),l++}b=e===l}else b=!0}}}}else{const e={params:{type:"object"}};null===a?a=[e]:a.push(e),l++}if(r!==l)break}}else{const e={params:{type:"array"}};null===a?a=[e]:a.push(e),l++}var g=u===l;if(f=f||g,!f){const t=l;if(l===t)if(e&&"object"==typeof e&&!Array.isArray(e))for(const t in e){let n=e[t];const r=l,o=l;let s=!1;const i=l;if(l===i)if(Array.isArray(n)){const e=n.length;for(let t=0;t<e;t++){let e=n[t];const r=l;if(l===r)if("string"==typeof e){if(e.length<1){const e={params:{}};null===a?a=[e]:a.push(e),l++}}else{const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}if(r!==l)break}}else{const e={params:{type:"array"}};null===a?a=[e]:a.push(e),l++}var v=i===l;if(s=s||v,!s){const e=l;if(!1!==n){const e={params:{}};null===a?a=[e]:a.push(e),l++}if(v=e===l,s=s||v,!s){const e=l;if(l===e)if("string"==typeof n){if(n.length<1){const e={params:{}};null===a?a=[e]:a.push(e),l++}}else{const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}v=e===l,s=s||v}}if(s)l=o,null!==a&&(o?a.length=o:a=null);else{const e={params:{}};null===a?a=[e]:a.push(e),l++}if(r!==l)break}else{const e={params:{type:"object"}};null===a?a=[e]:a.push(e),l++}g=t===l,f=f||g}if(f)l=p,null!==a&&(p?a.length=p:a=null);else{const e={params:{}};null===a?a=[e]:a.push(e),l++}if(i===l&&(o=!0,s=0),!o){const e={params:{passingSchemas:s}};return null===a?a=[e]:a.push(e),l++,se.errors=a,!1}l=r,null!==a&&(r?a.length=r:a=null),y=n===l}else y=!0;if(y){if(void 0!==t.fullySpecified){const e=l;if("boolean"!=typeof t.fullySpecified)return se.errors=[{params:{type:"boolean"}}],!1;y=e===l}else y=!0;if(y){if(void 0!==t.importsFields){let e=t.importsFields;const n=l;if(l===n){if(!Array.isArray(e))return se.errors=[{params:{type:"array"}}],!1;{const t=e.length;for(let n=0;n<t;n++){const t=l;if("string"!=typeof e[n])return se.errors=[{params:{type:"string"}}],!1;if(t!==l)break}}}y=n===l}else y=!0;if(y){if(void 0!==t.mainFields){let e=t.mainFields;const n=l;if(l===n){if(!Array.isArray(e))return se.errors=[{params:{type:"array"}}],!1;{const t=e.length;for(let n=0;n<t;n++){let t=e[n];const r=l,o=l;let s=!1;const i=l;if(l===i)if(Array.isArray(t)){const e=t.length;for(let n=0;n<e;n++){let e=t[n];const r=l;if(l===r)if("string"==typeof e){if(e.length<1){const e={params:{}};null===a?a=[e]:a.push(e),l++}}else{const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}if(r!==l)break}}else{const e={params:{type:"array"}};null===a?a=[e]:a.push(e),l++}var P=i===l;if(s=s||P,!s){const e=l;if(l===e)if("string"==typeof t){if(t.length<1){const e={params:{}};null===a?a=[e]:a.push(e),l++}}else{const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}P=e===l,s=s||P}if(!s){const e={params:{}};return null===a?a=[e]:a.push(e),l++,se.errors=a,!1}if(l=o,null!==a&&(o?a.length=o:a=null),r!==l)break}}}y=n===l}else y=!0;if(y){if(void 0!==t.mainFiles){let e=t.mainFiles;const n=l;if(l===n){if(!Array.isArray(e))return se.errors=[{params:{type:"array"}}],!1;{const t=e.length;for(let n=0;n<t;n++){let t=e[n];const r=l;if(l===r){if("string"!=typeof t)return se.errors=[{params:{type:"string"}}],!1;if(t.length<1)return se.errors=[{params:{}}],!1}if(r!==l)break}}}y=n===l}else y=!0;if(y){if(void 0!==t.modules){let e=t.modules;const n=l;if(l===n){if(!Array.isArray(e))return se.errors=[{params:{type:"array"}}],!1;{const t=e.length;for(let n=0;n<t;n++){let t=e[n];const r=l;if(l===r){if("string"!=typeof t)return se.errors=[{params:{type:"string"}}],!1;if(t.length<1)return se.errors=[{params:{}}],!1}if(r!==l)break}}}y=n===l}else y=!0;if(y){if(void 0!==t.plugins){let e=t.plugins;const n=l;if(l===n){if(!Array.isArray(e))return se.errors=[{params:{type:"array"}}],!1;{const t=e.length;for(let n=0;n<t;n++){let t=e[n];const r=l,o=l;let s=!1;const i=l;if("..."!==t){const e={params:{}};null===a?a=[e]:a.push(e),l++}var D=i===l;if(s=s||D,!s){const e=l;if(!1!==t&&0!==t&&""!==t&&null!=t){const e={params:{}};null===a?a=[e]:a.push(e),l++}if(D=e===l,s=s||D,!s){const e=l,n=l;let r=!1;const o=l;if(l===o)if(t&&"object"==typeof t&&!Array.isArray(t)){let e;if(void 0===t.apply&&(e="apply")){const t={params:{missingProperty:e}};null===a?a=[t]:a.push(t),l++}else if(void 0!==t.apply&&!(t.apply instanceof Function)){const e={params:{}};null===a?a=[e]:a.push(e),l++}}else{const e={params:{type:"object"}};null===a?a=[e]:a.push(e),l++}var O=o===l;if(r=r||O,!r){const e=l;if(!(t instanceof Function)){const e={params:{}};null===a?a=[e]:a.push(e),l++}O=e===l,r=r||O}if(r)l=n,null!==a&&(n?a.length=n:a=null);else{const e={params:{}};null===a?a=[e]:a.push(e),l++}D=e===l,s=s||D}}if(!s){const e={params:{}};return null===a?a=[e]:a.push(e),l++,se.errors=a,!1}if(l=o,null!==a&&(o?a.length=o:a=null),r!==l)break}}}y=n===l}else y=!0;if(y){if(void 0!==t.preferAbsolute){const e=l;if("boolean"!=typeof t.preferAbsolute)return se.errors=[{params:{type:"boolean"}}],!1;y=e===l}else y=!0;if(y){if(void 0!==t.preferRelative){const e=l;if("boolean"!=typeof t.preferRelative)return se.errors=[{params:{type:"boolean"}}],!1;y=e===l}else y=!0;if(y){if(void 0!==t.restrictions){let n=t.restrictions;const r=l;if(l===r){if(!Array.isArray(n))return se.errors=[{params:{type:"array"}}],!1;{const t=n.length;for(let r=0;r<t;r++){let t=n[r];const o=l,s=l;let i=!1;const p=l;if(!(t instanceof RegExp)){const e={params:{}};null===a?a=[e]:a.push(e),l++}var C=p===l;if(i=i||C,!i){const n=l;if(l===n)if("string"==typeof t){if(t.includes("!")||!0!==e.test(t)){const e={params:{}};null===a?a=[e]:a.push(e),l++}}else{const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}C=n===l,i=i||C}if(!i){const e={params:{}};return null===a?a=[e]:a.push(e),l++,se.errors=a,!1}if(l=s,null!==a&&(s?a.length=s:a=null),o!==l)break}}}y=r===l}else y=!0;if(y){if(void 0!==t.roots){let e=t.roots;const n=l;if(l===n){if(!Array.isArray(e))return se.errors=[{params:{type:"array"}}],!1;{const t=e.length;for(let n=0;n<t;n++){const t=l;if("string"!=typeof e[n])return se.errors=[{params:{type:"string"}}],!1;if(t!==l)break}}}y=n===l}else y=!0;if(y){if(void 0!==t.symlinks){const e=l;if("boolean"!=typeof t.symlinks)return se.errors=[{params:{type:"boolean"}}],!1;y=e===l}else y=!0;if(y){if(void 0!==t.tsconfig){let e=t.tsconfig;const n=l,r=l;let o=!1;const s=l;if("boolean"!=typeof e){const e={params:{type:"boolean"}};null===a?a=[e]:a.push(e),l++}var $=s===l;if(o=o||$,!o){const t=l;if("string"!=typeof e){const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}if($=t===l,o=o||$,!o){const t=l;if(l===t)if(e&&"object"==typeof e&&!Array.isArray(e)){const t=l;for(const t in e)if("configFile"!==t&&"references"!==t){const e={params:{additionalProperty:t}};null===a?a=[e]:a.push(e),l++;break}if(t===l){if(void 0!==e.configFile){const t=l;if("string"!=typeof e.configFile){const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}var A=t===l}else A=!0;if(A)if(void 0!==e.references){let t=e.references;const n=l,r=l;let o=!1;const s=l;if("auto"!==t){const e={params:{}};null===a?a=[e]:a.push(e),l++}var x=s===l;if(o=o||x,!o){const e=l;if("string"!=typeof t){const e={params:{type:"string"}};null===a?a=[e]:a.push(e),l++}x=e===l,o=o||x}if(o)l=r,null!==a&&(r?a.length=r:a=null);else{const e={params:{}};null===a?a=[e]:a.push(e),l++}A=n===l}else A=!0}}else{const e={params:{type:"object"}};null===a?a=[e]:a.push(e),l++}$=t===l,o=o||$}}if(!o){const e={params:{}};return null===a?a=[e]:a.push(e),l++,se.errors=a,!1}l=r,null!==a&&(r?a.length=r:a=null),y=n===l}else y=!0;if(y){if(void 0!==t.unsafeCache){let e=t.unsafeCache;const n=l,r=l;let o=!1;const s=l;if("boolean"!=typeof e){const e={params:{type:"boolean"}};null===a?a=[e]:a.push(e),l++}var k=s===l;if(o=o||k,!o){const t=l;if(l===t)if(e&&"object"==typeof e&&!Array.isArray(e));else{const e={params:{type:"object"}};null===a?a=[e]:a.push(e),l++}k=t===l,o=o||k}if(!o){const e={params:{}};return null===a?a=[e]:a.push(e),l++,se.errors=a,!1}l=r,null!==a&&(r?a.length=r:a=null),y=n===l}else y=!0;if(y)if(void 0!==t.useSyncFileSystemCalls){const e=l;if("boolean"!=typeof t.useSyncFileSystemCalls)return se.errors=[{params:{type:"boolean"}}],!1;y=e===l}else y=!0}}}}}}}}}}}}}}}}}}}}}}}}}}}}return se.errors=a,0===l}
```

### Buggy: 1 (Commit: 1b7584664da1e1e504ca30fd2630bb8f8ab2347a)
**Repo**: vue
```javascript
function genScopedSlot(el, state) {
    var isLegacySyntax = el.attrsMap['slot-scope']
    if (el.if && !el.ifProcessed && !isLegacySyntax) {
      return genIf(el, state, genScopedSlot, 'null')
    }
    if (el.for && !el.forProcessed) {
      return genFor(el, state, genScopedSlot)
    }
    var slotScope =
      el.slotScope === emptySlotScopeToken ? '' : String(el.slotScope)
    var fn =
      'function('.concat(slotScope, '){') +
      'return '.concat(
        el.tag === 'template'
          ? el.if && isLegacySyntax
            ? '('
                .concat(el.if, ')?')
                .concat(genChildren(el, state) || 'undefined', ':undefined')
            : genChildren(el, state) || 'undefined'
          : genElement(el, state),
        '}'
      )
    // reverse proxy v-slot without scope on this.$slots
    var reverseProxy = slotScope ? '' : ',proxy:true'
    return '{key:'
      .concat(el.slotTarget || '"default"', ',fn:')
      .concat(fn)
      .concat(reverseProxy, '}')
  }
```

### Buggy: 1 (Commit: a79c3cb5ef83a572d9319a8bef7ff17149566440)
**Repo**: webpack
```javascript
function figureOutScope(self, options, context = {}) {
		const { parent_scope: parentScope, toplevel = self } = context;
		options = defaults(options, {
			cache: null,
			ie8: false,
			safari10: false,
			module: false
		});
		if (!isToplevelNode(toplevel)) {
			throw new Error("Invalid toplevel scope");
		}

		// Pass 1: chain the scopes and define each declared name.
		/** @type {Node[]} */
		const stack = [];
		/** @type {boolean[]} */
		const strictOuter = [];
		let strict = Boolean(options.module);
		// The walk starts at this scope, which sets `scope` and `defun` first.
		let scope = /** @type {Scope} */ (self.parent_scope = parentScope);
		/** @type {Map<string, Node>} */
		let labels = new Map();
		let defun = /** @type {Scope} */ (/** @type {unknown} */ (null));
		/** @type {Node | null} */
		let inDestructuring = null;
		/** @type {Scope[]} */
		const forScopes = [];

		/**
		 * @param {number=} level how many parents up
		 * @returns {Node | undefined} that parent of the node visited
		 */
		const parent = (level) => stack[stack.length - 2 - (level || 0)];

		/**
		 * @param {SymbolDefinition} definition a definition just made
		 * @param {number} level where its declaration's statement is
		 * @returns {void}
		 */
		const markExport = (definition, level) => {
			if (inDestructuring) {
				let i = 0;
				do {
					level++;
				} while (parent(i++) !== inDestructuring);
			}
			const node = /** @type {Node} */ (parent(level));
			if ((definition.export = isExportNode(node) ? EXPORT_KEEP_NAME : 0)) {
				const exported = node.exported_definition;
				if (
					(isDefunNode(exported) || isDefClassNode(exported)) &&
					node.is_default
				) {
					definition.export = EXPORT_WANT_MANGLE;
				}
			}
		};

		const definer = {
			/**
			 * @param {Node} node the node visited
			 * @param {((node: Node, visitor: EXPECTED_ANY) => void)=} descend walks its children
			 * @returns {void}
			 */
			_visit(node, descend) {
				stack.push(node);
				const kind = kindBitsOf(node);
				const opensLevel = (kind & (SCOPE_LAMBDA | SCOPE_CLASS)) !== 0;
				if (opensLevel) {
					strictOuter.push(strict);
					if (kind & SCOPE_CLASS) strict = true;
				} else if (kind & SCOPE_DIRECTIVE && node.directive === "use strict") {
					strict = true;
				}
				if (!defineIn(node, kind, descend) && descend) {
					descend(node, this);
				}
				if (opensLevel) strict = /** @type {boolean} */ (strictOuter.pop());
				stack.pop();
			}
		};

		/**
		 * @param {Node} node the node visited
		 * @param {number} kind the classes it is, as `KIND` records them
		 * @param {((node: Node, visitor: EXPECTED_ANY) => void)=} descend walks its children
		 * @returns {boolean} true where the node's children are walked already
		 */
		const defineIn = (node, kind, descend) => {
			if (ast.isBlockScope(node)) {
				const saveScope = scope;
				// The scope copies its block's fields, a switch's cases or a catch's
				// statements as its `body`.
				node.block_scope = scope = ScopeNode(
					isSwitchNode(node) || isCatchNode(node)
						? {
								startToken: node.startToken,
								endToken: node.endToken,
								block_scope: node.block_scope,
								body: isSwitchNode(node) ? node.cases : node.body.body
							}
						: node
				);
				scope._block_scope = true;
				ast.initScopeVariables(scope, saveScope);
				scope.uses_with = saveScope.uses_with;
				scope.uses_eval = saveScope.uses_eval;
				if (
					options.safari10 &&
					(isForNode(node) || isForInNode(node) || isForOfNode(node))
				) {
					forScopes.push(scope);
				}
				if (isSwitchNode(node)) {
					// The switched expression belongs to the scope around the switch.
					const blockScope = scope;
					scope = saveScope;
					walkNode(node.discriminant, definer);
					scope = blockScope;
					for (let i = 0; i < node.cases.length; i++) {
						walkNode(node.cases[i], definer);
					}
				} else if (descend) {
					descend(node, definer);
				}
				scope = saveScope;
				return true;
			}
			if (kind & SCOPE_DESTRUCTURING) {
				const saveDestructuring = inDestructuring;
				inDestructuring = node;
				if (descend) descend(node, definer);
				inDestructuring = saveDestructuring;
				return true;
			}
			if (kind & SCOPE_SCOPE) {
				ast.initScopeVariables(node, scope);
				const saveScope = scope;
				const saveDefun = defun;
				const saveLabels = labels;
				defun = scope = node;
				labels = new Map();
				if (descend) descend(node, definer);
				scope = saveScope;
				defun = saveDefun;
				labels = saveLabels;
				if (kind & SCOPE_LAMBDA) detectScrewyArgnames(node, scope);
				return true;
			}
			if (kind & SCOPE_LABELED) {
				const label = node.label;
				if (labels.has(label.name)) {
					throw new Error(template("Label {name} defined twice", label));
				}
				labels.set(label.name, label);
				if (descend) descend(node, definer);
				labels.delete(label.name);
				return true;
			}
			if (kind & SCOPE_WITH) {
				for (let outer = scope; outer; outer = outer.parent_scope) {
					outer.uses_with = true;
				}
				return false;
			}
			if (kind & SCOPE_SYMBOL) node.scope = scope;
			if (kind & SCOPE_LABEL) {
				node.definition = node;
				node.references = [];
			}
			if (!(kind & SCOPE_DECLARES)) {
				// Neither declares a name nor refers to a label.
			} else if (isSymbolLambdaNode(node)) {
				ast.defineFunction(
					defun,
					node,
					node.name === "arguments" ? undefined : defun
				);
			} else if (isSymbolDefunNode(node)) {
				// A function declaration belongs to the scope around its own.
				const closestScope = defun.parent_scope;
				node.scope = strict ? closestScope : ast.getDefunScope(closestScope);
				markExport(ast.defineFunction(node.scope, node, defun), 1);
			} else if (isSymbolClassNode(node)) {
				markExport(ast.defineVariable(defun, node, defun), 1);
			} else if (isSymbolImportNode(node)) {
				ast.defineVariable(scope, node);
			} else if (isSymbolDefClassNode(node)) {
				markExport(
					ast.defineFunction((node.scope = defun.parent_scope), node, defun),
					1
				);
			} else if (
				isSymbolVarNode(node) ||
				isSymbolLetNode(node) ||
				isSymbolConstNode(node) ||
				isSymbolUsingNode(node) ||
				isSymbolCatchNode(node)
			) {
				const blockDeclaration = isSymbolBlockDeclarationNode(node);
				const definition = blockDeclaration
					? ast.defineVariable(scope, node, null)
					: ast.defineVariable(
							defun,
							node,
							isSymbolVarNode(node) && !isSymbolFunargNode(node)
								? null
								: undefined
						);
				if (
					!definition.orig.every((/** @type {Node} */ symbol) => {
						if (symbol === node) return true;
						if (blockDeclaration) return isSymbolLambdaNode(symbol);
						return !(
							isSymbolLetNode(symbol) ||
							isSymbolConstNode(symbol) ||
							isSymbolUsingNode(symbol)
						);
					})
				) {
					jsError(
						`"${node.name}" is redeclared`,
						node.startToken.file,
						node.startToken.line,
						node.startToken.col,
						node.startToken.pos
					);
				}
				if (!isSymbolFunargNode(node)) markExport(definition, 2);
				if (defun !== scope) {
					ast.markEnclosed(node);
					const found = ast.findVariable(scope, node);
					if (node.definition !== found) {
						node.definition = found;
						ast.addReference(node);
					}
				}
			} else if (isLabelRefNode(node)) {
				const symbol = labels.get(node.name);
				if (!symbol) {
					throw new Error(
						template("Undefined label {name} [{line},{col}]", {
							name: node.name,
							line: node.startToken.line,
							col: node.startToken.col
						})
					);
				}
				node.definition = symbol;
			}
			if (kind & SCOPE_MODULE_STATEMENT && !isToplevelNode(scope)) {
				jsError(
					`"${isExportNode(node) ? "Export" : ast.kindOf(node)}" statement may only appear at the top level`,
					node.startToken.file,
					node.startToken.line,
					node.startToken.col,
					node.startToken.pos
				);
			}
			return false;
		};

		walkNode(self, definer);

		// Pass 2: resolve each reference, and find `eval`.
		if (isToplevelNode(self)) self.globals = new Map();
		const resolver = {
			/**
			 * @param {Node} node the node visited
			 * @param {((node: Node, visitor: EXPECTED_ANY) => void)=} descend walks its children
			 * @returns {void}
			 */
			_visit(node, descend) {
				stack.push(node);
				if (!resolveIn(node) && descend) descend(node, this);
				stack.pop();
			}
		};

		/**
		 * @param {Node} node the node visited
		 * @returns {boolean} true where the node's children are not walked
		 */
		const resolveIn = (node) => {
			const kind = kindBitsOf(node);
			if (kind & SCOPE_LOOP_CONTROL && node.label) {
				node.label.definition.references.push(node);
				return true;
			}
			if (kind & SCOPE_REFERENCE) {
				const { name } = node;
				if (name === "eval" && isCallNode(parent())) {
					for (
						let outer = node.scope;
						outer && !outer.uses_eval;
						outer = outer.parent_scope
					) {
						outer.uses_eval = true;
					}
				}
				let symbol;
				if (
					(isNameMappingNode(parent()) &&
						/** @type {Node} */ (parent(1)).source) ||
					!(symbol = ast.findVariable(node.scope, name))
				) {
					symbol = ast.defineGlobal(toplevel, node);
					if (isSymbolExportNode(node)) {
						symbol.export = EXPORT_KEEP_NAME;
					}
				} else if (isLambdaNode(symbol.scope) && name === "arguments") {
					ast.getDefunScope(symbol.scope).uses_arguments = true;
				}
				node.definition = symbol;
				ast.addReference(node);
				if (
					ast.isBlockScope(node.scope) &&
					!isSymbolBlockDeclarationNode(symbol.orig[0])
				) {
					node.scope = ast.getDefunScope(node.scope);
				}
				return true;
			}
			// A catch parameter reusing a name of its function's scope.
			let definition;
			if (
				kind & SCOPE_CATCH &&
				(definition = redefinedCatchDefinition(node.definition))
			) {
				for (let outer = node.scope; outer; outer = outer.parent_scope) {
					encloseUnique(outer, definition);
					if (outer === definition.scope) break;
				}
			}
			return false;
		};

		walkNode(self, resolver);

		// Passes 3 and 4: work around old engines' catch and loop scopes.
		if (options.ie8 || options.safari10) {
			walk(self, (/** @type {Node} */ node) => {
				if (isSymbolCatchNode(node)) {
					const { name } = node;
					const references = node.definition.references;
					const defunScope = ast.getDefunScope(node.scope);
					const definition =
						ast.findVariable(defunScope, name) ||
						toplevel.globals.get(name) ||
						ast.defineVariable(defunScope, node);
					// forEach, as terser: referencing appends to the list it reads.
					// eslint-disable-next-line unicorn/no-array-for-each
					references.forEach((/** @type {Node} */ reference) => {
						reference.definition = definition;
						ast.addReference(reference);
					});
					node.definition = definition;
					ast.addReference(node);
					return true;
				}
			});
		}
		if (options.safari10) {
			for (const forScope of forScopes) {
				for (const definition of forScope.parent_scope.variables.values()) {
					encloseUnique(forScope, definition);
				}
			}
		}
	}
```

### Buggy: 1 (Commit: 1b7584664da1e1e504ca30fd2630bb8f8ab2347a)
**Repo**: vue
```javascript
function nodesToSegments(children, state) {
    var segments = []
    for (var i = 0; i < children.length; i++) {
      var c = children[i]
      if (c.type === 1) {
        segments.push.apply(segments, elementToSegments(c, state))
      } else if (c.type === 2) {
        segments.push({ type: INTERPOLATION, value: c.expression })
      } else if (c.type === 3) {
        var text = escape(c.text)
        if (c.isComment) {
          text = '<!--' + text + '-->'
        }
        segments.push({ type: RAW, value: text })
      }
    }
    return segments
  }
```

### Buggy: 1 (Commit: 1b7584664da1e1e504ca30fd2630bb8f8ab2347a)
**Repo**: vue
```javascript
function generateCodeFrame(source, start, end) {
  if (start === void 0) {
    start = 0
  }
  if (end === void 0) {
    end = source.length
  }
  var lines = source.split(/\r?\n/)
  var count = 0
  var res = []
  for (var i = 0; i < lines.length; i++) {
    count += lines[i].length + 1
    if (count >= start) {
      for (var j = i - range; j <= i + range || end > count; j++) {
        if (j < 0 || j >= lines.length) continue
        res.push(
          ''
            .concat(j + 1)
            .concat(repeat(' ', 3 - String(j + 1).length), '|  ')
            .concat(lines[j])
        )
        var lineLength = lines[j].length
        if (j === i) {
          // push underline
          var pad = start - (count - lineLength) + 1
          var length_1 = end > count ? lineLength - pad : end - start
          res.push('   |  ' + repeat(' ', pad) + repeat('^', length_1))
        } else if (j > i) {
          if (end > count) {
            var length_2 = Math.min(end - count, lineLength)
            res.push('   |  ' + repeat('^', length_2))
          }
          count += lineLength + 1
        }
      }
      break
    }
  }
  return res.join('\n')
}
```

### Buggy: 0 (Commit: 151ba3f5834a0909e8b9b1736f4889ac694c0104)
**Repo**: eslint
```javascript
onCodePathStart(codePath, node) {
				funcInfo = {
					upper: funcInfo,
					codePath,
					hasReturn: false,
					shouldCheck: isGetter(node),
					node,
					currentSegments: new Set(),
				};
			}
```

### Buggy: 1 (Commit: f4f3507460bc016b5be979c05d2969793f570cbf)
**Repo**: eslint
```javascript
*fix(fixer) {
							if (
								(!callbackInfo.isLexicalThis &&
									scopeInfo.this) ||
								hasDuplicateParams(node.params)
							) {
								/*
								 * If the callback function does not have .bind(this) and contains a reference to `this`, there
								 * is no way to determine what `this` should be, so don't perform any fixes.
								 * If the callback function has duplicates in its list of parameters (possible in sloppy mode),
								 * don't replace it with an arrow function, because this is a SyntaxError with arrow functions.
								 */
								return;
							}

							if (
								node.params.length &&
								node.params[0].name === "this"
							) {
								return;
							}

							// Remove `.bind(this)` if exists.
							if (callbackInfo.isLexicalThis) {
								const memberNode = node.parent;

								/*
								 * If `.bind(this)` exists but the parent is not `.bind(this)`, don't remove it automatically.
								 * E.g. `(foo || function(){}).bind(this)`
								 */
								if (memberNode.type !== "MemberExpression") {
									return;
								}

								const callNode = memberNode.parent;
								const firstTokenToRemove =
									sourceCode.getTokenAfter(
										memberNode.object,
										astUtils.isNotClosingParenToken,
									);
								const lastTokenToRemove =
									sourceCode.getLastToken(callNode);

								/*
								 * If the member expression is parenthesized, don't remove the right paren.
								 * E.g. `(function(){}.bind)(this)`
								 *                    ^^^^^^^^^^^^
								 */
								if (
									astUtils.isParenthesised(
										sourceCode,
										memberNode,
									)
								) {
									return;
								}

								// If comments exist in the `.bind(this)`, don't remove those.
								if (
									sourceCode.commentsExistBetween(
										firstTokenToRemove,
										lastTokenToRemove,
									)
								) {
									return;
								}

								yield fixer.removeRange([
									firstTokenToRemove.range[0],
									lastTokenToRemove.range[1],
								]);
							}

							// Convert the function expression to an arrow function.
							const functionToken = sourceCode.getFirstToken(
								node,
								node.async ? 1 : 0,
							);
							const leftParenToken = sourceCode.getTokenAfter(
								functionToken,
								astUtils.isOpeningParenToken,
							);
							const tokenBeforeBody = sourceCode.getTokenBefore(
								node.body,
							);

							if (
								sourceCode.commentsExistBetween(
									functionToken,
									leftParenToken,
								)
							) {
								// Remove only extra tokens to keep comments.
								yield fixer.remove(functionToken);
								if (node.id) {
									yield fixer.remove(node.id);
								}
							} else {
								// Remove extra tokens and spaces.
								yield fixer.removeRange([
									functionToken.range[0],
									leftParenToken.range[0],
								]);
							}
							yield fixer.insertTextAfter(tokenBeforeBody, " =>");

							// Get the node that will become the new arrow function.
							let replacedNode = callbackInfo.isLexicalThis
								? node.parent.parent
								: node;

							if (replacedNode.type === "ChainExpression") {
								replacedNode = replacedNode.parent;
							}

							/*
							 * If the replaced node is part of a BinaryExpression, LogicalExpression, or MemberExpression, then
							 * the arrow function needs to be parenthesized, because `foo || () => {}` is invalid syntax even
							 * though `foo || function() {}` is valid.
							 */
							if (
								replacedNode.parent.type !== "CallExpression" &&
								replacedNode.parent.type !==
									"ConditionalExpression" &&
								!astUtils.isParenthesised(
									sourceCode,
									replacedNode,
								) &&
								!astUtils.isParenthesised(sourceCode, node)
							) {
								yield fixer.insertTextBefore(replacedNode, "(");
								yield fixer.insertTextAfter(replacedNode, ")");
							}
						}
```

### Buggy: 1 (Commit: 73a7c552820291ee491e4dd8fa901cef113ec800)
**Repo**: axios
```javascript
formDataToStream = (form, headersHandler, options) => {
  const {
    tag = 'form-data-boundary',
    size = 25,
    boundary = tag + '-' + platform.generateString(size, BOUNDARY_ALPHABET),
  } = options || {};

  if (!utils.isFormData(form)) {
    throw TypeError('FormData instance required');
  }

  if (boundary.length < 1 || boundary.length > 70) {
    throw Error('boundary must be 1-70 characters long');
  }

  const boundaryBytes = textEncoder.encode('--' + boundary + CRLF);
  const footerBytes = textEncoder.encode('--' + boundary + '--' + CRLF);
  let contentLength = footerBytes.byteLength;

  const parts = Array.from(form.entries()).map(([name, value]) => {
    const part = new FormDataPart(name, value);
    contentLength += part.size;
    return part;
  });

  contentLength += boundaryBytes.byteLength * parts.length;

  contentLength = utils.toFiniteNumber(contentLength);

  const computedHeaders = {
    'Content-Type': `multipart/form-data; boundary=${boundary}`,
  };

  if (Number.isFinite(contentLength)) {
    computedHeaders['Content-Length'] = contentLength;
  }

  headersHandler && headersHandler(computedHeaders);

  return Readable.from(
    (async function* () {
      for (const part of parts) {
        yield boundaryBytes;
        yield* part.encode();
      }

      yield footerBytes;
    })()
  );
}
```

### Buggy: 1 (Commit: 490f1a1738449699c217e00ba56db378923fd6b5)
**Repo**: express
```javascript
function View(name, options) {
  var opts = options || {};

  this.defaultEngine = opts.defaultEngine;
  this.ext = extname(name);
  this.name = name;
  this.root = opts.root;

  if (!this.ext && !this.defaultEngine) {
    throw new Error('No default engine was specified and no extension was provided.');
  }

  var fileName = name;

  if (!this.ext) {
    // get extension from default engine name
    this.ext = this.defaultEngine[0] !== '.'
      ? '.' + this.defaultEngine
      : this.defaultEngine;

    fileName += this.ext;
  }

  if (!opts.engines[this.ext]) {
    // load engine
    var mod = this.ext.substr(1)
    debug('require "%s"', mod)

    // default engine export
    var fn = require(mod).__express

    if (typeof fn !== 'function') {
      throw new Error('Module "' + mod + '" does not provide a view engine.')
    }

    opts.engines[this.ext] = fn
  }

  // store loaded engine
  this.engine = opts.engines[this.ext];

  // lookup path
  this.path = this.lookup(fileName);
}
```

### Buggy: 0 (Commit: 15f7cd693e102c568df501eeeb9684f507e0ec0b)
**Repo**: react
```javascript
function completeBoundary(suspenseBoundaryID, contentID) {
  const contentNodeOuter = document.getElementById(contentID);
  if (!contentNodeOuter) {
    // If the client has failed hydration we may have already deleted the streaming
    // segments. The server may also have emitted a complete instruction but cancelled
    // the segment. Regardless we can ignore this case.
    return;
  }

  // Find the fallback's first element.
  const suspenseIdNodeOuter = document.getElementById(suspenseBoundaryID);
  if (!suspenseIdNodeOuter) {
    // We'll never reveal this boundary so we can remove its content immediately.
    // Otherwise we'll leave it in until we reveal it.
    // This is important in case this specific boundary contains other boundaries
    // that may get completed before we reveal this one.
    contentNodeOuter.parentNode.removeChild(contentNodeOuter);

    // The user must have already navigated away from this tree.
    // E.g. because the parent was hydrated. That's fine there's nothing to do
    // but we have to make sure that we already deleted the container node.
    return;
  }

  // Mark this Suspense boundary as queued so we know not to client render it
  // at the end of document load.
  const suspenseNodeOuter = suspenseIdNodeOuter.previousSibling;
  suspenseNodeOuter.data = SUSPENSE_QUEUED_START_DATA;
  // Queue this boundary for the next batch
  window['$RB'].push(suspenseIdNodeOuter, contentNodeOuter);

  if (window['$RB'].length === 2) {
    // This is the first time we've pushed to the batch. We need to schedule a callback
    // to flush the batch. This is delayed by the throttle heuristic.
    if (typeof window['$RT'] !== 'number') {
      // If we haven't had our rAF callback yet, schedule everything for the first paint.
      requestAnimationFrame(window['$RV'].bind(null, window['$RB']));
    } else {
      const currentTime = performance.now();
      const msUntilTimeout =
        // If the throttle would make us miss the target metric, then shorten the throttle.
        // performance.now()'s zero value is assumed to be the start time of the metric.
        currentTime < TARGET_VANITY_METRIC &&
        currentTime > TARGET_VANITY_METRIC - FALLBACK_THROTTLE_MS
          ? TARGET_VANITY_METRIC - currentTime
          : // Otherwise it's throttled starting from last commit time.
            window['$RT'] + FALLBACK_THROTTLE_MS - currentTime;
      // We always schedule the flush in a timer even if it's very low or negative to allow
      // for multiple completeBoundary calls that are already queued to have a chance to
      // make the batch.
      setTimeout(window['$RV'].bind(null, window['$RB']), msUntilTimeout);
    }
  }
}
```

### Buggy: 1 (Commit: 034f261fea1eed22d79706ef3c29666acc5fce4a)
**Repo**: express
```javascript
exports.hash = function (pwd, salt, fn) {
  if (3 == arguments.length) {
    crypto.pbkdf2(pwd, salt, iterations, len, function(err, hash){
      fn(err, hash.toString('base64'));
    });
  } else {
    fn = salt;
    crypto.randomBytes(len, function(err, salt){
      if (err) return fn(err);
      salt = salt.toString('base64');
      crypto.pbkdf2(pwd, salt, iterations, len, function(err, hash){
        if (err) return fn(err);
        fn(null, salt, hash.toString('base64'));
      });
    });
  }
}
```

### Buggy: 1 (Commit: 1b7584664da1e1e504ca30fd2630bb8f8ab2347a)
**Repo**: vue
```javascript
function processSlotOutlet(el) {
  if (el.tag === 'slot') {
    el.slotName = getBindingAttr(el, 'name')
    if (process.env.NODE_ENV !== 'production' && el.key) {
      warn$1(
        '`key` does not work on <slot> because slots are abstract outlets ' +
          'and can possibly expand into multiple elements. ' +
          'Use the key on a wrapping element instead.',
        getRawBindingAttr(el, 'key')
      )
    }
  }
}
```

### Buggy: 1 (Commit: 717e70843e68db648d2fc75c57d1a61465a9f7f9)
**Repo**: react
```javascript
function testJavaScript(render, patch) {
    it('reloads function declarations', async () => {
      if (__DEV__) {
        await render(`
          function Parent() {
            return <Child prop="A" />;
          };

          function Child({prop}) {
            return <h1>{prop}1</h1>;
          };

          export default Parent;
        `);
        const el = container.firstChild;
        expect(el.textContent).toBe('A1');
        await patch(`
          function Parent() {
            return <Child prop="B" />;
          };

          function Child({prop}) {
            return <h1>{prop}2</h1>;
          };

          export default Parent;
        `);
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('B2');
      }
    });

    it('reloads arrow functions', async () => {
      if (__DEV__) {
        await render(`
          const Parent = () => {
            return <Child prop="A" />;
          };

          const Child = ({prop}) => {
            return <h1>{prop}1</h1>;
          };

          export default Parent;
        `);
        const el = container.firstChild;
        expect(el.textContent).toBe('A1');
        await patch(`
          const Parent = () => {
            return <Child prop="B" />;
          };

          const Child = ({prop}) => {
            return <h1>{prop}2</h1>;
          };

          export default Parent;
        `);
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('B2');
      }
    });

    it('reloads a combination of memo and forwardRef', async () => {
      if (__DEV__) {
        await render(`
          const {memo} = React;

          const Parent = memo(React.forwardRef(function (props, ref) {
            return <Child prop="A" ref={ref} />;
          }));

          const Child = React.memo(({prop}) => {
            return <h1>{prop}1</h1>;
          });

          export default React.memo(Parent);
        `);
        const el = container.firstChild;
        expect(el.textContent).toBe('A1');
        await patch(`
          const {memo} = React;

          const Parent = memo(React.forwardRef(function (props, ref) {
            return <Child prop="B" ref={ref} />;
          }));

          const Child = React.memo(({prop}) => {
            return <h1>{prop}2</h1>;
          });

          export default React.memo(Parent);
        `);
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('B2');
      }
    });

    it('reloads default export with named memo', async () => {
      if (__DEV__) {
        await render(`
          const {memo} = React;

          const Child = React.memo(({prop}) => {
            return <h1>{prop}1</h1>;
          });

          export default memo(React.forwardRef(function Parent(props, ref) {
            return <Child prop="A" ref={ref} />;
          }));
        `);
        const el = container.firstChild;
        expect(el.textContent).toBe('A1');
        await patch(`
          const {memo} = React;

          const Child = React.memo(({prop}) => {
            return <h1>{prop}2</h1>;
          });

          export default memo(React.forwardRef(function Parent(props, ref) {
            return <Child prop="B" ref={ref} />;
          }));
        `);
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('B2');
      }
    });

    // @gate __DEV__ && enableActivity
    it('ignores ref for class component in hidden subtree', async () => {
      const code = `
        import {Activity} from 'react';

        // Avoid creating a new class on Fast Refresh.
        global.A = global.A ?? class A extends React.Component {
          render() {
            return <div />;
          }
        }
        const A = global.A;

        function hiddenRef() {
          throw new Error('Unexpected hiddenRef() invocation.');
        }

        export default function App() {
          return (
            <Activity mode="hidden">
              <A ref={hiddenRef} />
            </Activity>
          );
        };
      `;

      await render(code);
      await patch(code);
    });

    // @gate __DEV__ && enableActivity
    it('ignores ref for hoistable resource in hidden subtree', async () => {
      const code = `
        import {Activity} from 'react';

        function hiddenRef() {
          throw new Error('Unexpected hiddenRef() invocation.');
        }

        export default function App() {
          return (
            <Activity mode="hidden">
              <link rel="preload" href="foo" ref={hiddenRef} />
            </Activity>
          );
        };
      `;

      await render(code);
      await patch(code);
    });

    // @gate __DEV__ && enableActivity
    it('ignores ref for host component in hidden subtree', async () => {
      const code = `
        import {Activity} from 'react';

        function hiddenRef() {
          throw new Error('Unexpected hiddenRef() invocation.');
        }

        export default function App() {
          return (
            <Activity mode="hidden">
              <div ref={hiddenRef} />
            </Activity>
          );
        };
      `;

      await render(code);
      await patch(code);
    });

    // @gate __DEV__ && enableActivity
    it('ignores ref for Activity in hidden subtree', async () => {
      const code = `
        import {Activity} from 'react';

        function hiddenRef(value) {
          throw new Error('Unexpected hiddenRef() invocation.');
        }

        export default function App() {
          return (
            <Activity mode="hidden">
              <Activity mode="visible" ref={hiddenRef}>
                <div />
              </Activity>
            </Activity>
          );
        };
      `;

      await render(code);
      await patch(code);
    });

    // @gate __DEV__ && enableActivity && enableScopeAPI
    it('ignores ref for Scope in hidden subtree', async () => {
      const code = `
        import {
          Activity,
          unstable_Scope as Scope,
        } from 'react';

        function hiddenRef(value) {
          throw new Error('Unexpected hiddenRef() invocation.');
        }

        export default function App() {
          return (
            <Activity mode="hidden">
              <Scope ref={hiddenRef}>
                <div />
              </Scope>
            </Activity>
          );
        };
      `;

      await render(code);
      await patch(code);
    });

    // @gate __DEV__ && enableActivity
    it('ignores ref for functional component in hidden subtree', async () => {
      const code = `
        import {Activity} from 'react';

        // Avoid creating a new component on Fast Refresh.
        global.A = global.A ?? function A() {
          return <div />;
        }
        const A = global.A;

        function hiddenRef() {
          throw new Error('Unexpected hiddenRef() invocation.');
        }

        export default function App() {
          return (
            <Activity mode="hidden">
              <A ref={hiddenRef} />
            </Activity>
          );
        };
      `;

      await render(code);
      await patch(code);
    });

    // @gate __DEV__ && enableActivity
    it('ignores ref for ref forwarding component in hidden subtree', async () => {
      const code = `
        import {
          forwardRef,
          Activity,
        } from 'react';

        // Avoid creating a new component on Fast Refresh.
        global.A = global.A ?? forwardRef(function A(props, ref) {
          return <div ref={ref} />;
        });
        const A = global.A;

        function hiddenRef() {
          throw new Error('Unexpected hiddenRef() invocation.');
        }

        export default function App() {
          return (
            <Activity mode="hidden">
              <A ref={hiddenRef} />
            </Activity>
          );
        };
      `;

      await render(code);
      await patch(code);
    });

    // @gate __DEV__ && enableActivity
    it('ignores ref for simple memo component in hidden subtree', async () => {
      const code = `
        import {
          memo,
          Activity,
        } from 'react';

        // Avoid creating a new component on Fast Refresh.
        global.A = global.A ?? memo(function A() {
          return <div />;
        });
        const A = global.A;

        function hiddenRef() {
          throw new Error('Unexpected hiddenRef() invocation.');
        }

        export default function App() {
          return (
            <Activity mode="hidden">
              <A ref={hiddenRef} />
            </Activity>
          );
        };
      `;

      await render(code);
      await patch(code);
    });

    // @gate __DEV__ && enableActivity
    it('ignores ref for memo component in hidden subtree', async () => {
      // A custom compare function means this won't use SimpleMemoComponent.
      const code = `
        import {
          memo,
          Activity,
        } from 'react';

        // Avoid creating a new component on Fast Refresh.
        global.A = global.A ?? memo(
          function A() {
            return <div />;
          },
          () => false,
        );
        const A = global.A;

        function hiddenRef() {
          throw new Error('Unexpected hiddenRef() invocation.');
        }

        export default function App() {
          return (
            <Activity mode="hidden">
              <A ref={hiddenRef} />
            </Activity>
          );
        };
      `;

      await render(code);
      await patch(code);
    });

    it('reloads HOCs if they return functions', async () => {
      if (__DEV__) {
        await render(`
          function hoc(letter) {
            return function() {
              return <h1>{letter}1</h1>;
            }
          }

          export default function Parent() {
            return <Child />;
          }

          const Child = hoc('A');
        `);
        const el = container.firstChild;
        expect(el.textContent).toBe('A1');
        await patch(`
          function hoc(letter) {
            return function() {
              return <h1>{letter}2</h1>;
            }
          }

          export default function Parent() {
            return React.createElement(Child);
          }

          const Child = hoc('B');
        `);
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('B2');
      }
    });

    it('resets state when renaming a state variable', async () => {
      if (__DEV__) {
        await render(`
          const {useState} = React;
          const S = 1;

          export default function App() {
            const [foo, setFoo] = useState(S);
            return <h1>A{foo}</h1>;
          }
        `);
        const el = container.firstChild;
        expect(el.textContent).toBe('A1');

        await patch(`
          const {useState} = React;
          const S = 2;

          export default function App() {
            const [foo, setFoo] = useState(S);
            return <h1>B{foo}</h1>;
          }
        `);
        // Same state variable name, so state is preserved.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('B1');

        await patch(`
          const {useState} = React;
          const S = 3;

          export default function App() {
            const [bar, setBar] = useState(S);
            return <h1>C{bar}</h1>;
          }
        `);
        // Different state variable name, so state is reset.
        expect(container.firstChild).not.toBe(el);
        const newEl = container.firstChild;
        expect(newEl.textContent).toBe('C3');
      }
    });

    it('resets state when renaming a state variable in a HOC', async () => {
      if (__DEV__) {
        await render(`
          const {useState} = React;
          const S = 1;

          function hoc(Wrapped) {
            return function Generated() {
              const [foo, setFoo] = useState(S);
              return <Wrapped value={foo} />;
            };
          }

          export default hoc(({ value }) => {
            return <h1>A{value}</h1>;
          });
        `);
        const el = container.firstChild;
        expect(el.textContent).toBe('A1');

        await patch(`
          const {useState} = React;
          const S = 2;

          function hoc(Wrapped) {
            return function Generated() {
              const [foo, setFoo] = useState(S);
              return <Wrapped value={foo} />;
            };
          }

          export default hoc(({ value }) => {
            return <h1>B{value}</h1>;
          });
        `);
        // Same state variable name, so state is preserved.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('B1');

        await patch(`
          const {useState} = React;
          const S = 3;

          function hoc(Wrapped) {
            return function Generated() {
              const [bar, setBar] = useState(S);
              return <Wrapped value={bar} />;
            };
          }

          export default hoc(({ value }) => {
            return <h1>C{value}</h1>;
          });
        `);
        // Different state variable name, so state is reset.
        expect(container.firstChild).not.toBe(el);
        const newEl = container.firstChild;
        expect(newEl.textContent).toBe('C3');
      }
    });

    it('resets state when renaming a state variable in a HOC with indirection', async () => {
      if (__DEV__) {
        await render(`
          const {useState} = React;
          const S = 1;

          function hoc(Wrapped) {
            return function Generated() {
              const [foo, setFoo] = useState(S);
              return <Wrapped value={foo} />;
            };
          }

          function Indirection({ value }) {
            return <h1>A{value}</h1>;
          }

          export default hoc(Indirection);
        `);
        const el = container.firstChild;
        expect(el.textContent).toBe('A1');

        await patch(`
          const {useState} = React;
          const S = 2;

          function hoc(Wrapped) {
            return function Generated() {
              const [foo, setFoo] = useState(S);
              return <Wrapped value={foo} />;
            };
          }

          function Indirection({ value }) {
            return <h1>B{value}</h1>;
          }

          export default hoc(Indirection);
        `);
        // Same state variable name, so state is preserved.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('B1');

        await patch(`
          const {useState} = React;
          const S = 3;

          function hoc(Wrapped) {
            return function Generated() {
              const [bar, setBar] = useState(S);
              return <Wrapped value={bar} />;
            };
          }

          function Indirection({ value }) {
            return <h1>C{value}</h1>;
          }

          export default hoc(Indirection);
        `);
        // Different state variable name, so state is reset.
        expect(container.firstChild).not.toBe(el);
        const newEl = container.firstChild;
        expect(newEl.textContent).toBe('C3');
      }
    });

    it('resets state when renaming a state variable inside a HOC with direct call', async () => {
      if (__DEV__) {
        await render(`
          const {useState} = React;
          const S = 1;

          function hocWithDirectCall(Wrapped) {
            return function Generated() {
              return Wrapped();
            };
          }

          export default hocWithDirectCall(() => {
            const [foo, setFoo] = useState(S);
            return <h1>A{foo}</h1>;
          });
        `);
        const el = container.firstChild;
        expect(el.textContent).toBe('A1');

        await patch(`
          const {useState} = React;
          const S = 2;

          function hocWithDirectCall(Wrapped) {
            return function Generated() {
              return Wrapped();
            };
          }

          export default hocWithDirectCall(() => {
            const [foo, setFoo] = useState(S);
            return <h1>B{foo}</h1>;
          });
        `);
        // Same state variable name, so state is preserved.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('B1');

        await patch(`
          const {useState} = React;
          const S = 3;

          function hocWithDirectCall(Wrapped) {
            return function Generated() {
              return Wrapped();
            };
          }

          export default hocWithDirectCall(() => {
            const [bar, setBar] = useState(S);
            return <h1>C{bar}</h1>;
          });
        `);
        // Different state variable name, so state is reset.
        expect(container.firstChild).not.toBe(el);
        const newEl = container.firstChild;
        expect(newEl.textContent).toBe('C3');
      }
    });

    it('does not crash when changing Hook order inside a HOC with direct call', async () => {
      if (__DEV__) {
        await render(`
          const {useEffect} = React;

          function hocWithDirectCall(Wrapped) {
            return function Generated() {
              return Wrapped();
            };
          }

          export default hocWithDirectCall(() => {
            useEffect(() => {}, []);
            return <h1>A</h1>;
          });
        `);
        const el = container.firstChild;
        expect(el.textContent).toBe('A');

        await patch(`
          const {useEffect} = React;

          function hocWithDirectCall(Wrapped) {
            return function Generated() {
              return Wrapped();
            };
          }

          export default hocWithDirectCall(() => {
            useEffect(() => {}, []);
            useEffect(() => {}, []);
            return <h1>B</h1>;
          });
        `);
        // Hook order changed, so we remount.
        expect(container.firstChild).not.toBe(el);
        const newEl = container.firstChild;
        expect(newEl.textContent).toBe('B');
      }
    });

    it('does not crash when changing Hook order inside a memo-ed HOC with direct call', async () => {
      if (__DEV__) {
        await render(`
          const {useEffect, memo} = React;

          function hocWithDirectCall(Wrapped) {
            return memo(function Generated() {
              return Wrapped();
            });
          }

          export default hocWithDirectCall(() => {
            useEffect(() => {}, []);
            return <h1>A</h1>;
          });
        `);
        const el = container.firstChild;
        expect(el.textContent).toBe('A');

        await patch(`
          const {useEffect, memo} = React;

          function hocWithDirectCall(Wrapped) {
            return memo(function Generated() {
              return Wrapped();
            });
          }

          export default hocWithDirectCall(() => {
            useEffect(() => {}, []);
            useEffect(() => {}, []);
            return <h1>B</h1>;
          });
        `);
        // Hook order changed, so we remount.
        expect(container.firstChild).not.toBe(el);
        const newEl = container.firstChild;
        expect(newEl.textContent).toBe('B');
      }
    });

    it('does not crash when changing Hook order inside a memo+forwardRef-ed HOC with direct call', async () => {
      if (__DEV__) {
        await render(`
          const {useEffect, memo, forwardRef} = React;

          function hocWithDirectCall(Wrapped) {
            return memo(forwardRef(function Generated() {
              return Wrapped();
            }));
          }

          export default hocWithDirectCall(() => {
            useEffect(() => {}, []);
            return <h1>A</h1>;
          });
        `);
        const el = container.firstChild;
        expect(el.textContent).toBe('A');

        await patch(`
          const {useEffect, memo, forwardRef} = React;

          function hocWithDirectCall(Wrapped) {
            return memo(forwardRef(function Generated() {
              return Wrapped();
            }));
          }

          export default hocWithDirectCall(() => {
            useEffect(() => {}, []);
            useEffect(() => {}, []);
            return <h1>B</h1>;
          });
        `);
        // Hook order changed, so we remount.
        expect(container.firstChild).not.toBe(el);
        const newEl = container.firstChild;
        expect(newEl.textContent).toBe('B');
      }
    });

    it('does not crash when changing Hook order inside a HOC returning an object', async () => {
      if (__DEV__) {
        await render(`
          const {useEffect} = React;

          function hocWithDirectCall(Wrapped) {
            return {Wrapped: Wrapped};
          }

          export default hocWithDirectCall(() => {
            useEffect(() => {}, []);
            return <h1>A</h1>;
          }).Wrapped;
        `);
        const el = container.firstChild;
        expect(el.textContent).toBe('A');

        await patch(`
          const {useEffect} = React;

          function hocWithDirectCall(Wrapped) {
            return {Wrapped: Wrapped};
          }

          export default hocWithDirectCall(() => {
            useEffect(() => {}, []);
            useEffect(() => {}, []);
            return <h1>B</h1>;
          }).Wrapped;
        `);
        // Hook order changed, so we remount.
        expect(container.firstChild).not.toBe(el);
        const newEl = container.firstChild;
        expect(newEl.textContent).toBe('B');
      }
    });

    it('resets effects while preserving state', async () => {
      if (__DEV__) {
        await render(`
          const {useState} = React;

          export default function App() {
            const [value, setValue] = useState(0);
            return <h1>A{value}</h1>;
          }
        `);
        let el = container.firstChild;
        expect(el.textContent).toBe('A0');

        // Add an effect.
        await patch(`
          const {useState} = React;

          export default function App() {
            const [value, setValue] = useState(0);
            React.useEffect(() => {
              Scheduler.log('B mount');
              setValue(1)
              return () => {
                Scheduler.log('B unmount');
              };
            }, []);
            return <h1>B{value}</h1>;
          }
        `);

        // We added an effect, thereby changing Hook order.
        // This causes a remount.
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('B1');
        assertLog(['B mount']);

        await patch(`
          const {useState} = React;

          export default function App() {
            const [value, setValue] = useState(0);
            React.useEffect(() => {
              Scheduler.log('C mount');
              return () => {
                Scheduler.log('C unmount');
              };
            }, []);
            return <h1>C{value}</h1>;
          }
        `);
        // Same Hooks are called, so state is preserved.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('C1');

        // Effects are always reset, so effect B was unmounted and C was mounted.
        assertLog(['B unmount', 'C mount']);

        await patch(`
          const {useState} = React;

          export default function App() {
            const [value, setValue] = useState(0);
            return <h1>D{value}</h1>;
          }
        `);
        // Removing the effect changes the signature
        // and causes the component to remount.
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('D0');
        assertLog(['C unmount']);
      }
    });

    it('does not get confused when custom hooks are reordered', async () => {
      if (__DEV__) {
        await render(`
          function useFancyState(initialState) {
            return React.useState(initialState);
          }

          const App = () => {
            const [x, setX] = useFancyState('X');
            const [y, setY] = useFancyState('Y');
            return <h1>A{x}{y}</h1>;
          };

          export default App;
        `);
        let el = container.firstChild;
        expect(el.textContent).toBe('AXY');

        await patch(`
          function useFancyState(initialState) {
            return React.useState(initialState);
          }

          const App = () => {
            const [x, setX] = useFancyState('X');
            const [y, setY] = useFancyState('Y');
            return <h1>B{x}{y}</h1>;
          };

          export default App;
        `);
        // Same state variables, so no remount.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('BXY');

        await patch(`
          function useFancyState(initialState) {
            return React.useState(initialState);
          }

          const App = () => {
            const [y, setY] = useFancyState('Y');
            const [x, setX] = useFancyState('X');
            return <h1>B{x}{y}</h1>;
          };

          export default App;
        `);
        // Hooks were re-ordered. This causes a remount.
        // Therefore, Hook calls don't accidentally share state.
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('BXY');
      }
    });

    it('does not get confused when component is called early', async () => {
      if (__DEV__) {
        await render(`
          // This isn't really a valid pattern but it's close enough
          // to simulate what happens when you call ReactDOM.render
          // in the same file. We want to ensure this doesn't confuse
          // the runtime.
          App();

          function App() {
            const [x, setX] = useFancyState('X');
            const [y, setY] = useFancyState('Y');
            return <h1>A{x}{y}</h1>;
          };

          function useFancyState(initialState) {
            // No real Hook calls to avoid triggering invalid call invariant.
            // We only want to verify that we can still call this function early.
            return initialState;
          }

          export default App;
        `);
        let el = container.firstChild;
        expect(el.textContent).toBe('AXY');

        await patch(`
          // This isn't really a valid pattern but it's close enough
          // to simulate what happens when you call ReactDOM.render
          // in the same file. We want to ensure this doesn't confuse
          // the runtime.
          App();

          function App() {
            const [x, setX] = useFancyState('X');
            const [y, setY] = useFancyState('Y');
            return <h1>B{x}{y}</h1>;
          };

          function useFancyState(initialState) {
            // No real Hook calls to avoid triggering invalid call invariant.
            // We only want to verify that we can still call this function early.
            return initialState;
          }

          export default App;
        `);
        // Same state variables, so no remount.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('BXY');

        await patch(`
          // This isn't really a valid pattern but it's close enough
          // to simulate what happens when you call ReactDOM.render
          // in the same file. We want to ensure this doesn't confuse
          // the runtime.
          App();

          function App() {
            const [y, setY] = useFancyState('Y');
            const [x, setX] = useFancyState('X');
            return <h1>B{x}{y}</h1>;
          };

          function useFancyState(initialState) {
            // No real Hook calls to avoid triggering invalid call invariant.
            // We only want to verify that we can still call this function early.
            return initialState;
          }

          export default App;
        `);
        // Hooks were re-ordered. This causes a remount.
        // Therefore, Hook calls don't accidentally share state.
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('BXY');
      }
    });

    it('does not get confused by Hooks defined inline', async () => {
      // This is not a recommended pattern but at least it shouldn't break.
      if (__DEV__) {
        await render(`
          const App = () => {
            const useFancyState = (initialState) => {
              const result = React.useState(initialState);
              return result;
            };
            const [x, setX] = useFancyState('X1');
            const [y, setY] = useFancyState('Y1');
            return <h1>A{x}{y}</h1>;
          };

          export default App;
        `);
        let el = container.firstChild;
        expect(el.textContent).toBe('AX1Y1');

        await patch(`
          const App = () => {
            const useFancyState = (initialState) => {
              const result = React.useState(initialState);
              return result;
            };
            const [x, setX] = useFancyState('X2');
            const [y, setY] = useFancyState('Y2');
            return <h1>B{x}{y}</h1>;
          };

          export default App;
        `);
        // Remount even though nothing changed because
        // the custom Hook is inside -- and so we don't
        // really know whether its signature has changed.
        // We could potentially make it work, but for now
        // let's assert we don't crash with confusing errors.
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('BX2Y2');
      }
    });

    it('remounts component if custom hook it uses changes order', async () => {
      if (__DEV__) {
        await render(`
          const App = () => {
            const [x, setX] = useFancyState('X');
            const [y, setY] = useFancyState('Y');
            return <h1>A{x}{y}</h1>;
          };

          const useFancyState = (initialState) => {
            const result = useIndirection(initialState);
            return result;
          };

          function useIndirection(initialState) {
            return React.useState(initialState);
          }

          export default App;
        `);
        let el = container.firstChild;
        expect(el.textContent).toBe('AXY');

        await patch(`
          const App = () => {
            const [x, setX] = useFancyState('X');
            const [y, setY] = useFancyState('Y');
            return <h1>B{x}{y}</h1>;
          };

          const useFancyState = (initialState) => {
            const result = useIndirection();
            return result;
          };

          function useIndirection(initialState) {
            return React.useState(initialState);
          }

          export default App;
        `);
        // We didn't change anything except the header text.
        // So we don't expect a remount.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('BXY');

        await patch(`
          const App = () => {
            const [x, setX] = useFancyState('X');
            const [y, setY] = useFancyState('Y');
            return <h1>C{x}{y}</h1>;
          };

          const useFancyState = (initialState) => {
            const result = useIndirection(initialState);
            return result;
          };

          function useIndirection(initialState) {
            React.useEffect(() => {});
            return React.useState(initialState);
          }

          export default App;
        `);
        // The useIndirection Hook added an affect,
        // so we had to remount the component.
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('CXY');

        await patch(`
          const App = () => {
            const [x, setX] = useFancyState('X');
            const [y, setY] = useFancyState('Y');
            return <h1>D{x}{y}</h1>;
          };

          const useFancyState = (initialState) => {
            const result = useIndirection();
            return result;
          };

          function useIndirection(initialState) {
            React.useEffect(() => {});
            return React.useState(initialState);
          }

          export default App;
        `);
        // We didn't change anything except the header text.
        // So we don't expect a remount.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('DXY');
      }
    });

    it('does not lose the inferred arrow names', async () => {
      if (__DEV__) {
        await render(`
          const Parent = () => {
            return <Child/>;
          };

          const Child = () => {
            useMyThing();
            return <h1>{Parent.name} {Child.name} {useMyThing.name}</h1>;
          };

          const useMyThing = () => {
            React.useState();
          };

          export default Parent;
        `);
        expect(container.textContent).toBe('Parent Child useMyThing');
      }
    });

    it('does not lose the inferred function names', async () => {
      if (__DEV__) {
        await render(`
          var Parent = function() {
            return <Child/>;
          };

          var Child = function() {
            useMyThing();
            return <h1>{Parent.name} {Child.name} {useMyThing.name}</h1>;
          };

          var useMyThing = function() {
            React.useState();
          };

          export default Parent;
        `);
        expect(container.textContent).toBe('Parent Child useMyThing');
      }
    });

    it('resets state on every edit with @refresh reset annotation', async () => {
      if (__DEV__) {
        await render(`
          const {useState} = React;
          const S = 1;

          export default function App() {
            const [foo, setFoo] = useState(S);
            return <h1>A{foo}</h1>;
          }
        `);
        let el = container.firstChild;
        expect(el.textContent).toBe('A1');

        await patch(`
          const {useState} = React;
          const S = 2;

          export default function App() {
            const [foo, setFoo] = useState(S);
            return <h1>B{foo}</h1>;
          }
        `);
        // Same state variable name, so state is preserved.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('B1');

        await patch(`
          const {useState} = React;
          const S = 3;

          /* @refresh reset */

          export default function App() {
            const [foo, setFoo] = useState(S);
            return <h1>C{foo}</h1>;
          }
        `);
        // Found remount annotation, so state is reset.
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('C3');

        await patch(`
          const {useState} = React;
          const S = 4;

          export default function App() {

            // @refresh reset

            const [foo, setFoo] = useState(S);
            return <h1>D{foo}</h1>;
          }
        `);
        // Found remount annotation, so state is reset.
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('D4');

        await patch(`
          const {useState} = React;
          const S = 5;

          export default function App() {
            const [foo, setFoo] = useState(S);
            return <h1>E{foo}</h1>;
          }
        `);
        // There is no remount annotation anymore,
        // so preserve the previous state.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('E4');

        await patch(`
          const {useState} = React;
          const S = 6;

          export default function App() {
            const [foo, setFoo] = useState(S);
            return <h1>F{foo}</h1>;
          }
        `);
        // Continue editing.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('F4');

        await patch(`
          const {useState} = React;
          const S = 7;

          export default function App() {

            /* @refresh reset */

            const [foo, setFoo] = useState(S);
            return <h1>G{foo}</h1>;
          }
        `);
        // Force remount one last time.
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('G7');
      }
    });

    // This is best effort for simple cases.
    // We won't attempt to resolve identifiers.
    it('resets state when useState initial state is edited', async () => {
      if (__DEV__) {
        await render(`
          const {useState} = React;

          export default function App() {
            const [foo, setFoo] = useState(1);
            return <h1>A{foo}</h1>;
          }
        `);
        let el = container.firstChild;
        expect(el.textContent).toBe('A1');

        await patch(`
          const {useState} = React;

          export default function App() {
            const [foo, setFoo] = useState(1);
            return <h1>B{foo}</h1>;
          }
        `);
        // Same initial state, so it's preserved.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('B1');

        await patch(`
          const {useState} = React;

          export default function App() {
            const [foo, setFoo] = useState(2);
            return <h1>C{foo}</h1>;
          }
        `);
        // Different initial state, so state is reset.
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('C2');
      }
    });

    // This is best effort for simple cases.
    // We won't attempt to resolve identifiers.
    it('resets state when useReducer initial state is edited', async () => {
      if (__DEV__) {
        await render(`
          const {useReducer} = React;

          export default function App() {
            const [foo, setFoo] = useReducer(x => x, 1);
            return <h1>A{foo}</h1>;
          }
        `);
        let el = container.firstChild;
        expect(el.textContent).toBe('A1');

        await patch(`
          const {useReducer} = React;

          export default function App() {
            const [foo, setFoo] = useReducer(x => x, 1);
            return <h1>B{foo}</h1>;
          }
        `);
        // Same initial state, so it's preserved.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('B1');

        await patch(`
          const {useReducer} = React;

          export default function App() {
            const [foo, setFoo] = useReducer(x => x, 2);
            return <h1>C{foo}</h1>;
          }
        `);
        // Different initial state, so state is reset.
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('C2');
      }
    });

    it('remounts when switching export from function to class', async () => {
      if (__DEV__) {
        await render(`
          export default function App() {
            return <h1>A1</h1>;
          }
        `);
        let el = container.firstChild;
        expect(el.textContent).toBe('A1');
        await patch(`
          export default function App() {
            return <h1>A2</h1>;
          }
        `);
        // Keep state.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('A2');

        await patch(`
          export default class App extends React.Component {
            render() {
              return <h1>B1</h1>
            }
          }
        `);
        // Reset (function -> class).
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('B1');
        await patch(`
          export default class App extends React.Component {
            render() {
              return <h1>B2</h1>
            }
          }
        `);
        // Reset (classes always do).
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('B2');

        await patch(`
          export default function App() {
            return <h1>C1</h1>;
          }
        `);
        // Reset (class -> function).
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('C1');
        await patch(`
          export default function App() {
            return <h1>C2</h1>;
          }
        `);
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('C2');

        await patch(`
          export default function App() {
            return <h1>D1</h1>;
          }
        `);
        el = container.firstChild;
        expect(el.textContent).toBe('D1');
        await patch(`
          export default function App() {
            return <h1>D2</h1>;
          }
        `);
        // Keep state.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('D2');
      }
    });

    it('remounts when switching export from class to function', async () => {
      if (__DEV__) {
        await render(`
          export default class App extends React.Component {
            render() {
              return <h1>A1</h1>
            }
          }
        `);
        let el = container.firstChild;
        expect(el.textContent).toBe('A1');
        await patch(`
          export default class App extends React.Component {
            render() {
              return <h1>A2</h1>
            }
          }
        `);
        // Reset (classes always do).
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('A2');

        await patch(`
          export default function App() {
            return <h1>B1</h1>;
          }
        `);
        // Reset (class -> function).
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('B1');
        await patch(`
          export default function App() {
            return <h1>B2</h1>;
          }
        `);
        // Keep state.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('B2');

        await patch(`
          export default class App extends React.Component {
            render() {
              return <h1>C1</h1>
            }
          }
        `);
        // Reset (function -> class).
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('C1');
      }
    });

    it('remounts when wrapping export in a HOC', async () => {
      if (__DEV__) {
        await render(`
          export default function App() {
            return <h1>A1</h1>;
          }
        `);
        let el = container.firstChild;
        expect(el.textContent).toBe('A1');
        await patch(`
          export default function App() {
            return <h1>A2</h1>;
          }
        `);
        // Keep state.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('A2');

        await patch(`
          function hoc(Inner) {
            return function Wrapper() {
              return <Inner />;
            }
          }

          function App() {
            return <h1>B1</h1>;
          }

          export default hoc(App);
        `);
        // Reset (wrapped in HOC).
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('B1');
        await patch(`
          function hoc(Inner) {
            return function Wrapper() {
              return <Inner />;
            }
          }

          function App() {
            return <h1>B2</h1>;
          }

          export default hoc(App);
        `);
        // Keep state.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('B2');

        await patch(`
          export default function App() {
            return <h1>C1</h1>;
          }
        `);
        // Reset (unwrapped).
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('C1');
        await patch(`
          export default function App() {
            return <h1>C2</h1>;
          }
        `);
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('C2');
      }
    });

    it('remounts when wrapping export in memo()', async () => {
      if (__DEV__) {
        await render(`
          export default function App() {
            return <h1>A1</h1>;
          }
        `);
        let el = container.firstChild;
        expect(el.textContent).toBe('A1');
        await patch(`
          export default function App() {
            return <h1>A2</h1>;
          }
        `);
        // Keep state.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('A2');

        await patch(`
          function App() {
            return <h1>B1</h1>;
          }

          export default React.memo(App);
        `);
        // Reset (wrapped in HOC).
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('B1');
        await patch(`
          function App() {
            return <h1>B2</h1>;
          }

          export default React.memo(App);
        `);
        // Keep state.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('B2');

        await patch(`
          export default function App() {
            return <h1>C1</h1>;
          }
        `);
        // Reset (unwrapped).
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('C1');
        await patch(`
          export default function App() {
            return <h1>C2</h1>;
          }
        `);
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('C2');
      }
    });

    it('remounts when wrapping export in forwardRef()', async () => {
      if (__DEV__) {
        await render(`
          export default function App() {
            return <h1>A1</h1>;
          }
        `);
        let el = container.firstChild;
        expect(el.textContent).toBe('A1');
        await patch(`
          export default function App() {
            return <h1>A2</h1>;
          }
        `);
        // Keep state.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('A2');

        await patch(`
          function App() {
            return <h1>B1</h1>;
          }

          export default React.forwardRef(App);
        `);
        // Reset (wrapped in HOC).
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('B1');
        await patch(`
          function App() {
            return <h1>B2</h1>;
          }

          export default React.forwardRef(App);
        `);
        // Keep state.
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('B2');

        await patch(`
          export default function App() {
            return <h1>C1</h1>;
          }
        `);
        // Reset (unwrapped).
        expect(container.firstChild).not.toBe(el);
        el = container.firstChild;
        expect(el.textContent).toBe('C1');
        await patch(`
          export default function App() {
            return <h1>C2</h1>;
          }
        `);
        expect(container.firstChild).toBe(el);
        expect(el.textContent).toBe('C2');
      }
    });

    it('resets useMemoCache cache slots', async () => {
      if (__DEV__) {
        await render(`
          const useMemoCache = require('react/compiler-runtime').c;
          let cacheMisses = 0;
          const cacheMiss = (id) => {
            cacheMisses++;
            return id;
          };
          export default function App(t0) {
            const $ = useMemoCache(1);
            const {reset1} = t0;
            let t1;
            if ($[0] !== reset1) {
              $[0] = t1 = cacheMiss({reset1});
            } else {
              t1 = $[1];
            }
            return <h1>{cacheMisses}</h1>;
          }
        `);
        const el = container.firstChild;
        expect(el.textContent).toBe('1');
        await patch(`
          const useMemoCache = require('react/compiler-runtime').c;
          let cacheMisses = 0;
          const cacheMiss = (id) => {
            cacheMisses++;
            return id;
          };
          export default function App(t0) {
            const $ = useMemoCache(2);
            const {reset1, reset2} = t0;
            let t1;
            if ($[0] !== reset1) {
              $[0] = t1 = cacheMiss({reset1});
            } else {
              t1 = $[1];
            }
            let t2;
            if ($[1] !== reset2) {
              $[1] = t2 = cacheMiss({reset2});
            } else {
              t2 = $[1];
            }
            return <h1>{cacheMisses}</h1>;
          }
        `);
        expect(container.firstChild).toBe(el);
        // cache size changed between refreshes
        expect(el.textContent).toBe('2');
      }
    });

    describe('with inline requires', () => {
      beforeEach(() => {
        global.FakeModuleSystem = {};
      });

      afterEach(() => {
        delete global.FakeModuleSystem;
      });

      it('remounts component if custom hook it uses changes order on first edit', async () => {
        // This test verifies that remounting works even if calls to custom Hooks
        // were transformed with an inline requires transform, like we have on RN.
        // Inline requires make it harder to compare previous and next signatures
        // because useFancyState inline require always resolves to the newest version.
        // We're not actually using inline requires in the test, but it has similar semantics.
        if (__DEV__) {
          await render(`
            const FakeModuleSystem = global.FakeModuleSystem;

            FakeModuleSystem.useFancyState = function(initialState) {
              return React.useState(initialState);
            };

            const App = () => {
              const [x, setX] = FakeModuleSystem.useFancyState('X');
              const [y, setY] = FakeModuleSystem.useFancyState('Y');
              return <h1>A{x}{y}</h1>;
            };

            export default App;
          `);
          let el = container.firstChild;
          expect(el.textContent).toBe('AXY');

          await patch(`
            const FakeModuleSystem = global.FakeModuleSystem;

            FakeModuleSystem.useFancyState = function(initialState) {
              React.useEffect(() => {});
              return React.useState(initialState);
            };

            const App = () => {
              const [x, setX] = FakeModuleSystem.useFancyState('X');
              const [y, setY] = FakeModuleSystem.useFancyState('Y');
              return <h1>B{x}{y}</h1>;
            };

            export default App;
          `);
          // The useFancyState Hook added an effect,
          // so we had to remount the component.
          expect(container.firstChild).not.toBe(el);
          el = container.firstChild;
          expect(el.textContent).toBe('BXY');

          await patch(`
            const FakeModuleSystem = global.FakeModuleSystem;

            FakeModuleSystem.useFancyState = function(initialState) {
              React.useEffect(() => {});
              return React.useState(initialState);
            };

            const App = () => {
              const [x, setX] = FakeModuleSystem.useFancyState('X');
              const [y, setY] = FakeModuleSystem.useFancyState('Y');
              return <h1>C{x}{y}</h1>;
            };

            export default App;
          `);
          // We didn't change anything except the header text.
          // So we don't expect a remount.
          expect(container.firstChild).toBe(el);
          expect(el.textContent).toBe('CXY');
        }
      });

      it('remounts component if custom hook it uses changes order on second edit', async () => {
        if (__DEV__) {
          await render(`
            const FakeModuleSystem = global.FakeModuleSystem;

            FakeModuleSystem.useFancyState = function(initialState) {
              return React.useState(initialState);
            };

            const App = () => {
              const [x, setX] = FakeModuleSystem.useFancyState('X');
              const [y, setY] = FakeModuleSystem.useFancyState('Y');
              return <h1>A{x}{y}</h1>;
            };

            export default App;
          `);
          let el = container.firstChild;
          expect(el.textContent).toBe('AXY');

          await patch(`
            const FakeModuleSystem = global.FakeModuleSystem;

            FakeModuleSystem.useFancyState = function(initialState) {
              return React.useState(initialState);
            };

            const App = () => {
              const [x, setX] = FakeModuleSystem.useFancyState('X');
              const [y, setY] = FakeModuleSystem.useFancyState('Y');
              return <h1>B{x}{y}</h1>;
            };

            export default App;
          `);
          expect(container.firstChild).toBe(el);
          expect(el.textContent).toBe('BXY');

          await patch(`
            const FakeModuleSystem = global.FakeModuleSystem;

            FakeModuleSystem.useFancyState = function(initialState) {
              React.useEffect(() => {});
              return React.useState(initialState);
            };

            const App = () => {
              const [x, setX] = FakeModuleSystem.useFancyState('X');
              const [y, setY] = FakeModuleSystem.useFancyState('Y');
              return <h1>C{x}{y}</h1>;
            };

            export default App;
          `);
          // The useFancyState Hook added an effect,
          // so we had to remount the component.
          expect(container.firstChild).not.toBe(el);
          el = container.firstChild;
          expect(el.textContent).toBe('CXY');

          await patch(`
            const FakeModuleSystem = global.FakeModuleSystem;

            FakeModuleSystem.useFancyState = function(initialState) {
              React.useEffect(() => {});
              return React.useState(initialState);
            };

            const App = () => {
              const [x, setX] = FakeModuleSystem.useFancyState('X');
              const [y, setY] = FakeModuleSystem.useFancyState('Y');
              return <h1>D{x}{y}</h1>;
            };

            export default App;
          `);
          // We didn't change anything except the header text.
          // So we don't expect a remount.
          expect(container.firstChild).toBe(el);
          expect(el.textContent).toBe('DXY');
        }
      });

      it('recovers if evaluating Hook list throws', async () => {
        if (__DEV__) {
          await render(`
          let FakeModuleSystem = null;

          global.FakeModuleSystem.useFancyState = function(initialState) {
            return React.useState(initialState);
          };

          const App = () => {
            FakeModuleSystem = global.FakeModuleSystem;
            const [x, setX] = FakeModuleSystem.useFancyState('X');
            const [y, setY] = FakeModuleSystem.useFancyState('Y');
            return <h1>A{x}{y}</h1>;
          };

          export default App;
        `);
          let el = container.firstChild;
          expect(el.textContent).toBe('AXY');

          await patch(`
          let FakeModuleSystem = null;

          global.FakeModuleSystem.useFancyState = function(initialState) {
            React.useEffect(() => {});
            return React.useState(initialState);
          };

          const App = () => {
            FakeModuleSystem = global.FakeModuleSystem;
            const [x, setX] = FakeModuleSystem.useFancyState('X');
            const [y, setY] = FakeModuleSystem.useFancyState('Y');
            return <h1>B{x}{y}</h1>;
          };

          export default App;
        `);
          // We couldn't evaluate the Hook signatures
          // so we had to remount the component.
          expect(container.firstChild).not.toBe(el);
          el = container.firstChild;
          expect(el.textContent).toBe('BXY');
        }
      });

      it('remounts component if custom hook it uses changes order behind an indirection', async () => {
        if (__DEV__) {
          await render(`
            const FakeModuleSystem = global.FakeModuleSystem;

            FakeModuleSystem.useFancyState = function(initialState) {
              return FakeModuleSystem.useIndirection(initialState);
            };

            FakeModuleSystem.useIndirection = function(initialState) {
              return FakeModuleSystem.useOtherIndirection(initialState);
            };

            FakeModuleSystem.useOtherIndirection = function(initialState) {
              return React.useState(initialState);
            };

            const App = () => {
              const [x, setX] = FakeModuleSystem.useFancyState('X');
              const [y, setY] = FakeModuleSystem.useFancyState('Y');
              return <h1>A{x}{y}</h1>;
            };

            export default App;
          `);
          let el = container.firstChild;
          expect(el.textContent).toBe('AXY');

          await patch(`
            const FakeModuleSystem = global.FakeModuleSystem;

            FakeModuleSystem.useFancyState = function(initialState) {
              return FakeModuleSystem.useIndirection(initialState);
            };

            FakeModuleSystem.useIndirection = function(initialState) {
              return FakeModuleSystem.useOtherIndirection(initialState);
            };

            FakeModuleSystem.useOtherIndirection = function(initialState) {
              React.useEffect(() => {});
              return React.useState(initialState);
            };

            const App = () => {
              const [x, setX] = FakeModuleSystem.useFancyState('X');
              const [y, setY] = FakeModuleSystem.useFancyState('Y');
              return <h1>B{x}{y}</h1>;
            };

            export default App;
          `);

          // The useFancyState Hook added an effect,
          // so we had to remount the component.
          expect(container.firstChild).not.toBe(el);
          el = container.firstChild;
          expect(el.textContent).toBe('BXY');

          await patch(`
            const FakeModuleSystem = global.FakeModuleSystem;

            FakeModuleSystem.useFancyState = function(initialState) {
              return FakeModuleSystem.useIndirection(initialState);
            };

            FakeModuleSystem.useIndirection = function(initialState) {
              return FakeModuleSystem.useOtherIndirection(initialState);
            };

            FakeModuleSystem.useOtherIndirection = function(initialState) {
              React.useEffect(() => {});
              return React.useState(initialState);
            };

            const App = () => {
              const [x, setX] = FakeModuleSystem.useFancyState('X');
              const [y, setY] = FakeModuleSystem.useFancyState('Y');
              return <h1>C{x}{y}</h1>;
            };

            export default App;
          `);
          // We didn't change anything except the header text.
          // So we don't expect a remount.
          expect(container.firstChild).toBe(el);
          expect(el.textContent).toBe('CXY');
        }
      });
    });
  }
```

### Buggy: 1 (Commit: a79c3cb5ef83a572d9319a8bef7ff17149566440)
**Repo**: webpack
```javascript
ast.isDefaultAssignNode = (n) => isNode(n) && n.type === "AssignmentPattern"
```

### Buggy: 1 (Commit: da27d010ac6b4876f206f4cbd9daba69038d2c96)
**Repo**: webpack
```javascript
installOperatorOptimizers = (modules, helpers) => {
	const { transformNode } = modules.ast;
	const { ast, common, flags, inference, utils } = modules;
	const A = ast;
	const { PRECEDENCE, parse, JS_Parse_Error: JSParseError } = modules.parse;
	const { OutputStream } = modules.output;
	const { createCompressor } = modules.compress;
	const {
		make_sequence: makeSequence,
		best_of: bestOf,
		make_empty_function: makeEmptyFunction,
		make_node_from_constant: makeNodeFromConstant,
		merge_sequence: mergeSequence,
		maintain_this_binding: maintainThisBinding,
		is_identifier_atom: isIdentifierAtom
	} = common;
	const {
		is_undeclared_ref: isUndeclaredRef,
		bitwise_binop: bitwiseOperators,
		lazy_op: lazyOperators,
		is_nullish: isNullish,
		is_undefined: isUndefined
	} = inference;
	const { has_flag: hasFlag, set_flag: setFlag, UNUSED, TRUTHY, FALSY } = flags;
	const {
		make_void_0: makeVoid0,
		makePredicate,
		regexp_source_fix: regexpSourceFix,
		regexp_is_safe: regexpIsSafe
	} = utils;
	const {
		defineOptimizer,
		inlineArrayLikeSpread,
		unsafeUndefinedRef,
		inlineIntoCall
	} = helpers;
	const firstInStatement =
		/** @type {(compressor: CompressorShape) => boolean | undefined} */ (
			createFirstInStatement(modules)
		);
	const commutativeOperators = makePredicate("== === != !== * & | ^");
	const unsafeConstructors = ["Object", "RegExp", "Function", "Error", "Array"];

	/**
	 * terser's `is_object`.
	 * @param {Node} node a node
	 * @returns {boolean} whether it is an array, function, object or class literal
	 */
	const isObject = (node) =>
		A.isArrayNode(node) ||
		A.isLambdaNode(node) ||
		A.isObjectNode(node) ||
		A.isClassNode(node);

	/**
	 * terser's `[…].join(…)` folding, from inside its `CallNode` optimizer.
	 * @param {Node} self the call
	 * @param {Node} expression its callee, a `.join` read of an array literal
	 * @param {CompressorShape} compressor the compressor
	 * @returns {Node | null} what replaces the call, or null to go on
	 */
	const optimizeJoin = (self, expression, compressor) => {
		let separator;
		if (self.arguments.length > 0) {
			separator = ast.evaluate(self.arguments[0], compressor);
			if (separator === self.arguments[0]) return null;
		}
		/** @type {(Node | null)[]} */
		const elements = [];
		/** @type {EXPECTED_ANY[]} */
		const constants = [];
		for (
			let i = 0, length = expression.object.elements.length;
			i < length;
			i++
		) {
			const element = expression.object.elements[i];
			if (A.isExpansionNode(element)) return null;
			// A hole evaluates as terser's hole node did: undefined, or itself.
			const value =
				element === null
					? compressor.option("evaluate")
						? undefined
						: null
					: ast.evaluate(element, compressor);
			if (value !== element) {
				constants.push(value);
			} else {
				if (constants.length > 0) {
					elements.push(
						makeNode(A.StringNode, self, { value: constants.join(separator) })
					);
					constants.length = 0;
				}
				elements.push(element);
			}
		}
		if (constants.length > 0) {
			elements.push(
				makeNode(A.StringNode, self, { value: constants.join(separator) })
			);
		}
		if (elements.length === 0) {
			return makeNode(A.StringNode, self, { value: "" });
		}
		if (elements.length === 1) {
			if (elements[0] !== null && ast.isString(elements[0], compressor)) {
				return elements[0];
			}
			return makeNode(A.BinaryNode, /** @type {Node} */ (elements[0]), {
				operator: "+",
				left: makeNode(A.StringNode, self, { value: "" }),
				right: elements[0]
			});
		}
		// A separator of `0`, `false` or `[]` joins with "" here too.
		// eslint-disable-next-line eqeqeq
		if (separator == "") {
			// The separator evaluated, so each hole did too.
			const joined = /** @type {Node[]} */ (elements);
			const first =
				ast.isString(joined[0], compressor) ||
				ast.isString(joined[1], compressor)
					? /** @type {Node} */ (joined.shift())
					: makeNode(A.StringNode, self, { value: "" });
			return ast.optimize(
				joined.reduce(
					(previous, element) =>
						makeNode(A.BinaryNode, element, {
							operator: "+",
							left: previous,
							right: element
						}),
					first
				),
				compressor
			);
		}
		// Cloned down to the array so the original stays intact for `best_of`.
		const node = ast.cloneNode(self);
		node.callee = ast.cloneNode(node.callee);
		node.callee.object = ast.cloneNode(node.callee.object);
		node.callee.object.elements = elements;
		return bestOf(compressor, self, node);
	};

	defineOptimizer("Call", (self, compressor) => {
		const expression = self.callee;
		let fn = expression;
		inlineArrayLikeSpread(self.arguments);
		const simpleArgs = self.arguments.every(
			(/** @type {Node} */ argument) => !A.isExpansionNode(argument)
		);

		if (compressor.option("reduce_vars") && A.isSymbolRefNode(fn)) {
			fn = ast.fixedValue(fn);
		}

		const isFunction = A.isLambdaNode(fn);

		if (isFunction && ast.isPinned(fn)) return self;

		if (
			compressor.option("unused") &&
			simpleArgs &&
			isFunction &&
			!fn.uses_arguments
		) {
			let position = 0;
			let last = 0;
			for (let i = 0, length = self.arguments.length; i < length; i++) {
				if (A.isExpansionNode(fn.params[i])) {
					if (hasFlag(fn.params[i].argument, UNUSED)) {
						while (i < length) {
							const node = ast.dropSideEffectFree(
								self.arguments[i++],
								compressor
							);
							if (node) {
								self.arguments[position++] = node;
							}
						}
					} else {
						while (i < length) {
							self.arguments[position++] = self.arguments[i++];
						}
					}
					last = position;
					break;
				}
				const trim = i >= fn.params.length;
				if (trim || hasFlag(fn.params[i], UNUSED)) {
					const node = ast.dropSideEffectFree(self.arguments[i], compressor);
					if (node) {
						self.arguments[position++] = node;
					} else if (!trim) {
						self.arguments[position++] = makeNode(
							A.NumberNode,
							self.arguments[i],
							{
								value: 0
							}
						);
						continue;
					}
				} else {
					self.arguments[position++] = self.arguments[i];
				}
				last = position;
			}
			self.arguments.length = last;
		}

		if (
			A.isDotNode(expression) &&
			A.isSymbolRefNode(expression.object) &&
			expression.object.name === "console" &&
			expression.object.definition.undeclared &&
			expression.property.name === "assert"
		) {
			const condition = self.arguments[0];
			if (condition) {
				const value = ast.evaluate(condition, compressor);

				if (value === 1 || value === true) {
					return ast.optimize(makeVoid0(self), compressor);
				}
			}
		}

		if (compressor.option("unsafe") && !ast.containsOptional(expression)) {
			if (
				A.isDotNode(expression) &&
				expression.startToken.value === "Array" &&
				expression.property.name === "from" &&
				self.arguments.length === 1
			) {
				const [argument] = self.arguments;
				if (A.isArrayNode(argument)) {
					return ast.optimize(
						makeNode(A.ArrayNode, argument, {
							elements: argument.elements
						}),
						compressor
					);
				}
			}
			if (isUndeclaredRef(expression)) {
				switch (expression.name) {
					case "Array":
						if (self.arguments.length !== 1) {
							return ast.optimize(
								makeNode(A.ArrayNode, self, {
									elements: self.arguments
								}),
								compressor
							);
						} else if (
							A.isNumberNode(self.arguments[0]) &&
							self.arguments[0].value <= 11
						) {
							const elements = [];
							for (let i = 0; i < self.arguments[0].value; i++) {
								elements.push(null);
							}
							return A.ArrayNode({ elements });
						}
						break;
					case "Object":
						if (self.arguments.length === 0) {
							return makeNode(A.ObjectNode, self, {
								properties: []
							});
						}
						break;
					case "String":
						if (self.arguments.length === 0) {
							return makeNode(A.StringNode, self, {
								value: ""
							});
						}
						if (self.arguments.length <= 1) {
							return ast.optimize(
								makeNode(A.BinaryNode, self, {
									left: self.arguments[0],
									operator: "+",
									right: makeNode(A.StringNode, self, { value: "" })
								}),
								compressor
							);
						}
						break;
					case "Number":
						if (self.arguments.length === 0) {
							return makeNode(A.NumberNode, self, {
								value: 0
							});
						}
						if (
							self.arguments.length === 1 &&
							compressor.option("unsafe_math")
						) {
							return ast.optimize(
								makeNode(A.UnaryPrefixNode, self, {
									argument: self.arguments[0],
									operator: "+"
								}),
								compressor
							);
						}
						break;
					case "Symbol":
						if (
							self.arguments.length === 1 &&
							A.isStringNode(self.arguments[0]) &&
							compressor.option("unsafe_symbols")
						) {
							self.arguments.length = 0;
						}
						break;
					case "Boolean":
						if (self.arguments.length === 0) return makeNode(A.FalseNode, self);
						if (self.arguments.length === 1) {
							return ast.optimize(
								makeNode(A.UnaryPrefixNode, self, {
									argument: makeNode(A.UnaryPrefixNode, self, {
										argument: self.arguments[0],
										operator: "!"
									}),
									operator: "!"
								}),
								compressor
							);
						}
						break;
					case "RegExp": {
						/** @type {EXPECTED_ANY[]} */
						const params = [];
						if (
							self.arguments.length >= 1 &&
							self.arguments.length <= 2 &&
							self.arguments.every((/** @type {Node} */ argument) => {
								const value = ast.evaluate(argument, compressor);
								params.push(value);
								return argument !== value;
							}) &&
							regexpIsSafe(params[0])
						) {
							let [source] = params;
							const regexpFlags = params[1];
							source = regexpSourceFix(new RegExp(source).source);
							const regexp = makeNode(A.RegExpNode, self, {
								value: { source, flags: regexpFlags }
							});
							if (ast.evaluateNode(regexp, compressor) !== regexp) {
								return regexp;
							}
						}
						break;
					}
				}
			} else if (A.isDotNode(expression)) {
				switch (expression.property.name) {
					case "toString":
						if (
							self.arguments.length === 0 &&
							!ast.mayThrowOnAccess(expression.object, compressor)
						) {
							return ast.optimize(
								makeNode(A.BinaryNode, self, {
									left: makeNode(A.StringNode, self, { value: "" }),
									operator: "+",
									right: expression.object
								}),
								compressor
							);
						}
						break;
					case "join":
						if (A.isArrayNode(expression.object)) {
							const joined = optimizeJoin(self, expression, compressor);
							if (joined) return joined;
						}
						break;
					case "charAt":
						if (ast.isString(expression.object, compressor)) {
							const argument = self.arguments[0];
							const index = argument ? ast.evaluate(argument, compressor) : 0;
							if (index !== argument) {
								return ast.optimize(
									makeNode(A.SubNode, expression, {
										object: expression.object,
										property: makeNodeFromConstant(
											index | 0,
											argument || expression
										),
										computed: true
									}),
									compressor
								);
							}
						}
						break;
					case "apply":
						if (
							self.arguments.length === 2 &&
							A.isArrayNode(self.arguments[1])
						) {
							const args = [...self.arguments[1].elements];
							args.unshift(self.arguments[0]);
							return ast.optimize(
								makeNode(A.CallNode, self, {
									callee: makeNode(A.DotNode, expression, {
										object: expression.object,
										optional: false,
										property: A.SymbolPropertyNode({ name: "call" }),
										computed: false
									}),
									arguments: args
								}),
								compressor
							);
						}
						break;
					case "call": {
						let func = expression.object;
						if (A.isSymbolRefNode(func)) {
							func = ast.fixedValue(func);
						}
						if (A.isLambdaNode(func) && !ast.containsThis(func)) {
							// terser passes its optimizer's `this`, undefined, so no position.
							return ast.optimize(
								self.arguments.length
									? makeSequence(undefined, [
											self.arguments[0],
											makeNode(A.CallNode, self, {
												callee: expression.object,
												arguments: self.arguments.slice(1)
											})
										])
									: makeNode(A.CallNode, self, {
											callee: expression.object,
											arguments: []
										}),
								compressor
							);
						}
						break;
					}
				}
			}
		}

		if (
			compressor.option("unsafe_Function") &&
			isUndeclaredRef(expression) &&
			expression.name === "Function"
		) {
			if (self.arguments.length === 0) {
				return ast.optimize(makeEmptyFunction(self), compressor);
			}
			if (
				self.arguments.every((/** @type {Node} */ argument) =>
					A.isStringNode(argument)
				)
			) {
				// A constant `new Function` body is minified as a function of its own:
				// https://github.com/mishoo/UglifyJS2/issues/203
				try {
					const code = `n(function(${self.arguments
						.slice(0, -1)
						.map((/** @type {Node} */ argument) => argument.value)
						.join(",")}){${self.arguments[self.arguments.length - 1].value}})`;
					let program = parse(code);
					const mangle = compressor.mangle_options();
					ast.figureOutScope(program, mangle);
					const innerCompressor = createCompressor(compressor.options, {
						mangle_options: compressor._mangle_options
					});
					assignNativeLookups(innerCompressor, modules.nativeObjects);
					program = transformNode(program, innerCompressor);
					const functionNode = /** @type {PrintFunction} */ (
						modules.mangledFunctionOf(program, mangle)
					);
					const stream = OutputStream();
					modules.printFunctionBody(functionNode, stream);
					self.arguments = [
						makeNode(A.StringNode, self, {
							value: functionNode.params
								.map((parameter) => modules.printEstreeToString(parameter))
								.join(",")
						}),
						makeNode(A.StringNode, self.arguments[self.arguments.length - 1], {
							value: stream.get().replace(/^\{|\}$/g, "")
						})
					];
					return self;
				} catch (error) {
					// Any other error is left to throw when the code runs.
					if (!(error instanceof JSParseError)) {
						throw error;
					}
				}
			}
		}

		return inlineIntoCall(self, compressor);
	});

	/**
	 * @param {Node} self a node
	 * @returns {boolean} whether it holds an optional property read or call
	 */
	ast.containsOptional = function containsOptional(self) {
		if (A.isPropAccessNode(self) || A.isCallNode(self) || A.isChainNode(self)) {
			if (self.optional) {
				return true;
			}
			return ast.containsOptional(
				A.isCallNode(self)
					? self.callee
					: A.isPropAccessNode(self)
						? self.object
						: self.expression
			);
		}
		return false;
	};

	defineOptimizer("New", (self, compressor) => {
		if (
			compressor.option("unsafe") &&
			isUndeclaredRef(self.callee) &&
			unsafeConstructors.includes(self.callee.name)
		) {
			return transformNode(makeNode(A.CallNode, self, self), compressor);
		}
		return self;
	});

	defineOptimizer("Sequence", (self, compressor) => {
		if (!compressor.option("side_effects")) return self;
		/** @type {Node[]} */
		const expressions = [];
		let first = firstInStatement(compressor);
		const last = self.expressions.length - 1;
		for (let index = 0; index <= last; index++) {
			/** @type {Node | null} */ let expression = self.expressions[index];
			if (index < last) {
				expression = ast.dropSideEffectFree(expression, compressor, first);
			}
			if (expression) {
				mergeSequence(expressions, expression);
				first = false;
			}
		}
		let end = expressions.length - 1;
		while (end > 0 && isUndefined(expressions[end], compressor)) end--;
		if (end < expressions.length - 1) {
			expressions[end] = makeNode(A.UnaryPrefixNode, self, {
				operator: "void",
				argument: expressions[end]
			});
			expressions.length = end + 1;
		}
		if (end === 0) {
			self = maintainThisBinding(
				compressor.parent(),
				compressor.self(),
				expressions[0]
			);
			if (!A.isSequenceNode(self)) self = ast.optimize(self, compressor);
			return self;
		}
		self.expressions = expressions;
		return self;
	});

	/**
	 * @param {Node} self a unary operation
	 * @param {CompressorShape} compressor the compressor
	 * @returns {Node} a sequence ending in the operation, where its operand was one
	 */
	const liftUnarySequences = (self, compressor) => {
		if (compressor.option("sequences") && A.isSequenceNode(self.argument)) {
			const expressions = [...self.argument.expressions];
			const clone = ast.cloneNode(self);
			clone.argument = /** @type {Node} */ (expressions.pop());
			expressions.push(clone);
			return ast.optimize(makeSequence(self, expressions), compressor);
		}
		return self;
	};

	defineOptimizer("UnaryPostfix", (self, compressor) =>
		liftUnarySequences(self, compressor)
	);

	defineOptimizer("UnaryPrefix", (self, compressor) => {
		/** @type {Node} */ let expression = self.argument;
		if (
			self.operator === "delete" &&
			!(
				A.isSymbolRefNode(expression) ||
				A.isPropAccessNode(expression) ||
				A.isChainNode(expression) ||
				isIdentifierAtom(expression)
			)
		) {
			return ast.optimize(
				makeSequence(self, [expression, makeNode(A.TrueNode, self)]),
				compressor
			);
		}
		if (
			self.operator === "void" &&
			A.isNumberNode(expression) &&
			expression.value === 0
		) {
			return unsafeUndefinedRef(self, compressor) || self;
		}
		const sequence = liftUnarySequences(self, compressor);
		if (sequence !== self) {
			return sequence;
		}
		if (compressor.option("side_effects") && self.operator === "void") {
			const kept = ast.dropSideEffectFree(expression, compressor);
			if (kept) {
				self.argument = kept;
				return self;
			}
			return ast.optimize(makeVoid0(self), compressor);
		}
		if (compressor.in_boolean_context()) {
			switch (self.operator) {
				case "!":
					if (A.isUnaryPrefixNode(expression) && expression.operator === "!") {
						return expression.argument;
					}
					if (A.isBinaryNode(expression)) {
						self = bestOf(
							compressor,
							self,
							ast.negate(expression, compressor, firstInStatement(compressor))
						);
					}
					break;
				case "typeof":
					// `typeof` yields a non-empty string, even of an undeclared name.
					return ast.optimize(
						A.isSymbolRefNode(expression)
							? makeNode(A.TrueNode, self)
							: makeSequence(self, [expression, makeNode(A.TrueNode, self)]),
						compressor
					);
			}
		}
		if (self.operator === "-" && A.isInfinityNode(expression)) {
			expression = transformNode(expression, compressor);
		}
		if (
			A.isBinaryNode(expression) &&
			(self.operator === "+" || self.operator === "-") &&
			(expression.operator === "*" ||
				expression.operator === "/" ||
				expression.operator === "%")
		) {
			return makeNode(A.BinaryNode, self, {
				operator: expression.operator,
				left: makeNode(A.UnaryPrefixNode, expression.left, {
					operator: self.operator,
					argument: expression.left
				}),
				right: expression.right
			});
		}

		if (compressor.option("evaluate")) {
			// ~~x => x, where only 32 bits are read or x has no more
			if (
				self.operator === "~" &&
				A.isUnaryPrefixNode(self.argument) &&
				self.argument.operator === "~" &&
				(compressor.in_32_bit_context(false) ||
					ast.is32BitInteger(self.argument.argument, compressor))
			) {
				return self.argument.argument;
			}

			// ~(x ^ y) => x ^ ~y, and ~(~x ^ y) => x ^ y
			if (
				self.operator === "~" &&
				A.isBinaryNode(expression) &&
				expression.operator === "^"
			) {
				if (
					A.isUnaryPrefixNode(expression.left) &&
					expression.left.operator === "~"
				) {
					expression.left = ast.bitwiseNegate(
						expression.left,
						compressor,
						true
					);
				} else {
					expression.right = ast.bitwiseNegate(
						expression.right,
						compressor,
						true
					);
				}
				return expression;
			}
		}

		if (
			self.operator !== "-" ||
			// A negative number literal would fold into itself forever.
			!(
				A.isNumberNode(expression) ||
				A.isInfinityNode(expression) ||
				A.isBigIntNode(expression)
			)
		) {
			let evaluated = ast.evaluate(self, compressor);
			if (evaluated !== self) {
				evaluated = ast.optimize(
					makeNodeFromConstant(evaluated, self),
					compressor
				);
				return bestOf(compressor, evaluated, self);
			}
		}
		return self;
	});

	/**
	 * @param {Node} self a binary operation
	 * @param {CompressorShape} compressor the compressor
	 * @returns {Node} a sequence ending in the operation, where an operand was one
	 */
	ast.liftBinarySequences = (self, compressor) => {
		if (compressor.option("sequences")) {
			if (A.isSequenceNode(self.left)) {
				const expressions = [...self.left.expressions];
				const clone = ast.cloneNode(self);
				clone.left = /** @type {Node} */ (expressions.pop());
				expressions.push(clone);
				return ast.optimize(makeSequence(self, expressions), compressor);
			}
			if (
				A.isSequenceNode(self.right) &&
				!ast.hasSideEffects(self.left, compressor)
			) {
				const assign = self.operator === "=" && A.isSymbolRefNode(self.left);
				const expressions = self.right.expressions;
				const last = expressions.length - 1;
				let i = 0;
				for (; i < last; i++) {
					if (!assign && ast.hasSideEffects(expressions[i], compressor)) break;
				}
				if (i === last) {
					const lifted = [...expressions];
					const clone = ast.cloneNode(self);
					clone.right = /** @type {Node} */ (lifted.pop());
					lifted.push(clone);
					return ast.optimize(makeSequence(self, lifted), compressor);
				} else if (i > 0) {
					const clone = ast.cloneNode(self);
					clone.right = makeSequence(self.right, expressions.slice(i));
					const lifted = expressions.slice(0, i);
					lifted.push(clone);
					return ast.optimize(makeSequence(self, lifted), compressor);
				}
			}
		}
		return self;
	};

	defineOptimizer("Binary", (self, compressor) => {
		/**
		 * @returns {boolean} whether swapping the operands keeps what runs
		 */
		const reversible = () =>
			ast.isConstant(self.left) ||
			ast.isConstant(self.right) ||
			(!ast.hasSideEffects(self.left, compressor) &&
				!ast.hasSideEffects(self.right, compressor));
		/**
		 * @param {string=} operator the operator after the swap
		 * @returns {void}
		 */
		const reverse = (operator) => {
			if (reversible()) {
				if (operator) self.operator = operator;
				const left = self.left;
				self.left = self.right;
				self.right = left;
			}
		};
		if (
			compressor.option("lhs_constants") &&
			commutativeOperators.has(self.operator) &&
			ast.isConstant(self.right) &&
			!ast.isConstant(self.left) &&
			// A constant right cannot see what the left does, so they may swap.
			!(
				A.isBinaryNode(self.left) &&
				PRECEDENCE[self.left.operator] >= PRECEDENCE[self.operator]
			)
		) {
			reverse();
		}
		self = ast.liftBinarySequences(self, compressor);
		if (compressor.option("comparisons")) {
			/** @type {boolean | undefined} */
			let isStrictComparison;
			switch (self.operator) {
				case "===":
				case "!==":
					isStrictComparison = true;
					if (
						(ast.isString(self.left, compressor) &&
							ast.isString(self.right, compressor)) ||
						(ast.isNumber(self.left, compressor) &&
							ast.isNumber(self.right, compressor)) ||
						(ast.isBigInt(self.left, compressor) &&
							ast.isBigInt(self.right, compressor)) ||
						(ast.isBoolean(self.left) && ast.isBoolean(self.right)) ||
						ast.isEquivalent(self.left, self.right)
					) {
						self.operator = self.operator.slice(0, 2);
					}
				// falls through
				case "==":
				case "!=":
					if (!isStrictComparison && isUndefined(self.left, compressor)) {
						// void 0 == x => null == x
						self.left = makeNode(A.NullNode, self.left);
					} else if (
						!isStrictComparison &&
						isUndefined(self.right, compressor)
					) {
						self.right = makeNode(A.NullNode, self.right);
					} else if (
						compressor.option("typeofs") &&
						// "undefined" == typeof x => undefined === x
						A.isStringNode(self.left) &&
						self.left.value === "undefined" &&
						A.isUnaryPrefixNode(self.right) &&
						self.right.operator === "typeof"
					) {
						const expression = self.right.argument;
						if (
							A.isSymbolRefNode(expression)
								? ast.isDeclared(expression, compressor)
								: !(A.isPropAccessNode(expression) && compressor.option("ie8"))
						) {
							self.right = expression;
							self.left = ast.optimize(makeVoid0(self.left), compressor);
							if (self.operator.length === 2) self.operator += "=";
						}
					} else if (
						compressor.option("typeofs") &&
						A.isUnaryPrefixNode(self.left) &&
						self.left.operator === "typeof" &&
						A.isStringNode(self.right) &&
						self.right.value === "undefined"
					) {
						const expression = self.left.argument;
						if (
							A.isSymbolRefNode(expression)
								? ast.isDeclared(expression, compressor)
								: !(A.isPropAccessNode(expression) && compressor.option("ie8"))
						) {
							self.left = expression;
							self.right = ast.optimize(makeVoid0(self.right), compressor);
							if (self.operator.length === 2) self.operator += "=";
						}
					} else if (
						A.isSymbolRefNode(self.left) &&
						// obj !== obj => false
						A.isSymbolRefNode(self.right) &&
						self.left.definition === self.right.definition &&
						isObject(ast.fixedValue(self.left))
					) {
						return makeNode(
							self.operator[0] === "=" ? A.TrueNode : A.FalseNode,
							self
						);
					} else if (
						ast.is32BitInteger(self.left, compressor) &&
						ast.is32BitInteger(self.right, compressor)
					) {
						/**
						 * @param {Node} node an operand
						 * @returns {Node} its negation
						 */
						const logicalNot = (node) =>
							makeNode(A.UnaryPrefixNode, node, {
								operator: "!",
								argument: node
							});
						/**
						 * @param {Node} node an operand
						 * @param {boolean} truthy whether to test it for truthiness
						 * @returns {Node} the test, as a boolean where one is read
						 */
						const asBooleanValue = (node, truthy) => {
							if (truthy) {
								return compressor.in_boolean_context()
									? node
									: logicalNot(logicalNot(node));
							}
							return logicalNot(node);
						};

						// The only falsy 32-bit integer is 0
						if (A.isNumberNode(self.left) && self.left.value === 0) {
							return asBooleanValue(self.right, self.operator[0] === "!");
						}
						if (A.isNumberNode(self.right) && self.right.value === 0) {
							return asBooleanValue(self.left, self.operator[0] === "!");
						}

						// (x & 0xFF) != 0xFF => !(~x & 0xFF)
						const andOperation = A.isBinaryNode(self.left)
							? self.left
							: A.isBinaryNode(self.right)
								? self.right
								: null;
						if (andOperation) {
							const mask = andOperation === self.left ? self.right : self.left;
							if (
								mask &&
								andOperation.operator === "&" &&
								A.isNumberNode(mask) &&
								ast.is32BitInteger(mask, compressor)
							) {
								const operand = ast.isEquivalent(andOperation.left, mask)
									? andOperation.right
									: ast.isEquivalent(andOperation.right, mask)
										? andOperation.left
										: null;
								if (operand) {
									const optimized = asBooleanValue(
										makeNode(A.BinaryNode, self, {
											operator: "&",
											left: mask,
											right: makeNode(A.UnaryPrefixNode, self, {
												operator: "~",
												argument: operand
											})
										}),
										self.operator[0] === "!"
									);

									return bestOf(compressor, optimized, self);
								}
							}
						}
					}
					break;
				case "&&":
				case "||": {
					let lhs = self.left;
					if (lhs.operator === self.operator) {
						lhs = lhs.right;
					}
					if (
						A.isBinaryNode(lhs) &&
						lhs.operator === (self.operator === "&&" ? "!==" : "===") &&
						A.isBinaryNode(self.right) &&
						lhs.operator === self.right.operator &&
						((isUndefined(lhs.left, compressor) &&
							A.isNullNode(self.right.left)) ||
							(A.isNullNode(lhs.left) &&
								isUndefined(self.right.left, compressor))) &&
						!ast.hasSideEffects(lhs.right, compressor) &&
						ast.isEquivalent(lhs.right, self.right.right)
					) {
						let combined = makeNode(A.BinaryNode, self, {
							operator: lhs.operator.slice(0, -1),
							left: makeNode(A.NullNode, self),
							right: lhs.right
						});
						if (lhs !== self.left) {
							combined = makeNode(A.BinaryNode, self, {
								operator: self.operator,
								left: self.left.left,
								right: combined
							});
						}
						return combined;
					}
					break;
				}
			}
		}
		if (self.operator === "+" && compressor.in_boolean_context()) {
			const leftValue = ast.evaluate(self.left, compressor);
			const rightValue = ast.evaluate(self.right, compressor);
			if (leftValue && typeof leftValue === "string") {
				return ast.optimize(
					makeSequence(self, [self.right, makeNode(A.TrueNode, self)]),
					compressor
				);
			}
			if (rightValue && typeof rightValue === "string") {
				return ast.optimize(
					makeSequence(self, [self.left, makeNode(A.TrueNode, self)]),
					compressor
				);
			}
		}
		if (compressor.option("comparisons") && ast.isBoolean(self)) {
			if (
				!A.isBinaryNode(compressor.parent()) ||
				A.isAssignNode(compressor.parent())
			) {
				const negated = makeNode(A.UnaryPrefixNode, self, {
					operator: "!",
					argument: ast.negate(self, compressor, firstInStatement(compressor))
				});
				self = bestOf(compressor, self, negated);
			}
			if (compressor.option("unsafe_comps")) {
				switch (self.operator) {
					case "<":
						reverse(">");
						break;
					case "<=":
						reverse(">=");
						break;
				}
			}
		}
		if (self.operator === "+") {
			if (
				A.isStringNode(self.right) &&
				ast.constantValue(self.right) === "" &&
				ast.isString(self.left, compressor)
			) {
				return self.left;
			}
			if (
				A.isStringNode(self.left) &&
				ast.constantValue(self.left) === "" &&
				ast.isString(self.right, compressor)
			) {
				return self.right;
			}
			if (
				A.isBinaryNode(self.left) &&
				self.left.operator === "+" &&
				A.isStringNode(self.left.left) &&
				ast.constantValue(self.left.left) === "" &&
				ast.isString(self.right, compressor)
			) {
				self.left = self.left.right;
				return self;
			}
		}
		if (compressor.option("evaluate")) {
			switch (self.operator) {
				case "&&": {
					const leftValue = hasFlag(self.left, TRUTHY)
						? true
						: hasFlag(self.left, FALSY)
							? false
							: ast.evaluate(self.left, compressor);
					if (!leftValue) {
						return ast.optimize(
							maintainThisBinding(
								compressor.parent(),
								compressor.self(),
								self.left
							),
							compressor
						);
					} else if (!A.isSyntaxNode(leftValue)) {
						return ast.optimize(
							makeSequence(self, [self.left, self.right]),
							compressor
						);
					}
					const rightValue = ast.evaluate(self.right, compressor);
					if (!rightValue) {
						if (compressor.in_boolean_context()) {
							return ast.optimize(
								makeSequence(self, [self.left, makeNode(A.FalseNode, self)]),
								compressor
							);
						}
						setFlag(self, FALSY);
					} else if (!A.isSyntaxNode(rightValue)) {
						const parent = compressor.parent();
						if (
							(parent.operator === "&&" && parent.left === compressor.self()) ||
							compressor.in_boolean_context()
						) {
							return ast.optimize(self.left, compressor);
						}
					}
					// x || false && y ---> x ? y : false
					if (self.left.operator === "||") {
						const leftRightValue = ast.evaluate(self.left.right, compressor);
						if (!leftRightValue) {
							return ast.optimize(
								makeNode(A.ConditionalNode, self, {
									test: self.left.left,
									consequent: self.right,
									alternate: self.left.right
								}),
								compressor
							);
						}
					}
					break;
				}
				case "||": {
					const leftValue = hasFlag(self.left, TRUTHY)
						? true
						: hasFlag(self.left, FALSY)
							? false
							: ast.evaluate(self.left, compressor);
					if (!leftValue) {
						return ast.optimize(
							makeSequence(self, [self.left, self.right]),
							compressor
						);
					} else if (!A.isSyntaxNode(leftValue)) {
						return ast.optimize(
							maintainThisBinding(
								compressor.parent(),
								compressor.self(),
								self.left
							),
							compressor
						);
					}
					const rightValue = ast.evaluate(self.right, compressor);
					if (!rightValue) {
						const parent = compressor.parent();
						if (
							(parent.operator === "||" && parent.left === compressor.self()) ||
							compressor.in_boolean_context()
						) {
							return ast.optimize(self.left, compressor);
						}
					} else if (!A.isSyntaxNode(rightValue)) {
						if (compressor.in_boolean_context()) {
							return ast.optimize(
								makeSequence(self, [self.left, makeNode(A.TrueNode, self)]),
								compressor
							);
						}
						setFlag(self, TRUTHY);
					}
					if (self.left.operator === "&&") {
						const leftRightValue = ast.evaluate(self.left.right, compressor);
						if (leftRightValue && !A.isSyntaxNode(leftRightValue)) {
							return ast.optimize(
								makeNode(A.ConditionalNode, self, {
									test: self.left.left,
									consequent: self.left.right,
									alternate: self.right
								}),
								compressor
							);
						}
					}
					break;
				}
				case "??": {
					if (isNullish(self.left, compressor)) {
						return self.right;
					}

					const leftValue = ast.evaluate(self.left, compressor);
					if (!A.isSyntaxNode(leftValue)) {
						return leftValue === null || leftValue === undefined
							? self.right
							: self.left;
					}

					if (compressor.in_boolean_context()) {
						const rightValue = ast.evaluate(self.right, compressor);
						if (!A.isSyntaxNode(rightValue) && !rightValue) {
							return self.left;
						}
					}
				}
			}
			let associative = true;
			switch (self.operator) {
				case "+":
					// (x + "foo") + "bar" => x + "foobar"
					if (
						A.isConstantNode(self.right) &&
						A.isBinaryNode(self.left) &&
						self.left.operator === "+" &&
						ast.isString(self.left, compressor)
					) {
						const binary = makeNode(A.BinaryNode, self, {
							operator: "+",
							left: self.left.right,
							right: self.right
						});
						const optimized = ast.optimize(binary, compressor);
						if (binary !== optimized) {
							self = makeNode(A.BinaryNode, self, {
								operator: "+",
								left: self.left.left,
								right: optimized
							});
						}
					}
					// (x + "foo") + ("bar" + y) => (x + "foobar") + y
					if (
						A.isBinaryNode(self.left) &&
						self.left.operator === "+" &&
						ast.isString(self.left, compressor) &&
						A.isBinaryNode(self.right) &&
						self.right.operator === "+" &&
						ast.isString(self.right, compressor)
					) {
						const binary = makeNode(A.BinaryNode, self, {
							operator: "+",
							left: self.left.right,
							right: self.right.left
						});
						const optimized = ast.optimize(binary, compressor);
						if (binary !== optimized) {
							self = makeNode(A.BinaryNode, self, {
								operator: "+",
								left: makeNode(A.BinaryNode, self.left, {
									operator: "+",
									left: self.left.left,
									right: optimized
								}),
								right: self.right.right
							});
						}
					}
					// a + -b => a - b
					if (
						A.isUnaryPrefixNode(self.right) &&
						self.right.operator === "-" &&
						ast.isNumberOrBigInt(self.left, compressor)
					) {
						self = makeNode(A.BinaryNode, self, {
							operator: "-",
							left: self.left,
							right: self.right.argument
						});
						break;
					}
					// -a + b => b - a
					if (
						A.isUnaryPrefixNode(self.left) &&
						self.left.operator === "-" &&
						reversible() &&
						ast.isNumberOrBigInt(self.right, compressor)
					) {
						self = makeNode(A.BinaryNode, self, {
							operator: "-",
							left: self.right,
							right: self.left.argument
						});
						break;
					}
					// `foo${bar}baz` + 1 => `foo${bar}baz1`
					if (A.isTemplateStringNode(self.left)) {
						const left = self.left;
						const right = ast.evaluate(self.right, compressor);
						// Loose, as terser: a node reads as its string form.
						// eslint-disable-next-line eqeqeq
						if (right != self.right) {
							left.segments[left.segments.length - 1].value += String(right);
							return left;
						}
					}
					// 1 + `foo${bar}baz` => `1foo${bar}baz`
					if (A.isTemplateStringNode(self.right)) {
						const right = self.right;
						const left = ast.evaluate(self.left, compressor);
						// eslint-disable-next-line eqeqeq
						if (left != self.left) {
							right.segments[0].value = String(left) + right.segments[0].value;
							return right;
						}
					}
					// `1${bar}2` + `foo${bar}baz` => `1${bar}2foo${bar}baz`
					if (
						A.isTemplateStringNode(self.left) &&
						A.isTemplateStringNode(self.right)
					) {
						const left = self.left;
						const segments = left.segments;
						const right = self.right;
						segments[segments.length - 1].value += right.segments[0].value;
						for (let i = 1; i < right.segments.length; i++) {
							segments.push(right.segments[i]);
						}
						return left;
					}
				// falls through
				case "*":
					associative = compressor.option("unsafe_math");
				// falls through
				case "&":
				case "|":
				case "^":
					// a + +b => +b + a
					if (
						ast.isNumberOrBigInt(self.left, compressor) &&
						ast.isNumberOrBigInt(self.right, compressor) &&
						reversible() &&
						!(
							A.isBinaryNode(self.left) &&
							self.left.operator !== self.operator &&
							PRECEDENCE[self.left.operator] >= PRECEDENCE[self.operator]
						)
					) {
						const reversed = makeNode(A.BinaryNode, self, {
							operator: self.operator,
							left: self.right,
							right: self.left
						});
						self =
							A.isConstantNode(self.right) && !A.isConstantNode(self.left)
								? bestOf(compressor, reversed, self)
								: bestOf(compressor, self, reversed);
					}
					if (associative && ast.isNumberOrBigInt(self, compressor)) {
						// a + (b + c) => (a + b) + c
						if (
							A.isBinaryNode(self.right) &&
							self.right.operator === self.operator
						) {
							self = makeNode(A.BinaryNode, self, {
								operator: self.operator,
								left: makeNode(A.BinaryNode, self.left, {
									operator: self.operator,
									left: self.left,
									right: self.right.left,
									startToken: self.left.startToken,
									endToken: self.right.left.endToken
								}),
								right: self.right.right
							});
						}
						// (n + 2) + 3 => 5 + n, and (2 * n) * 3 => 6 * n
						if (
							A.isConstantNode(self.right) &&
							A.isBinaryNode(self.left) &&
							self.left.operator === self.operator
						) {
							if (A.isConstantNode(self.left.left)) {
								self = makeNode(A.BinaryNode, self, {
									operator: self.operator,
									left: makeNode(A.BinaryNode, self.left, {
										operator: self.operator,
										left: self.left.left,
										right: self.right,
										startToken: self.left.left.startToken,
										endToken: self.right.endToken
									}),
									right: self.left.right
								});
							} else if (A.isConstantNode(self.left.right)) {
								self = makeNode(A.BinaryNode, self, {
									operator: self.operator,
									left: makeNode(A.BinaryNode, self.left, {
										operator: self.operator,
										left: self.left.right,
										right: self.right,
										startToken: self.left.right.startToken,
										endToken: self.right.endToken
									}),
									right: self.left.left
								});
							}
						}
						// (a | 1) | (2 | d) => (3 | a) | d
						if (
							A.isBinaryNode(self.left) &&
							self.left.operator === self.operator &&
							A.isConstantNode(self.left.right) &&
							A.isBinaryNode(self.right) &&
							self.right.operator === self.operator &&
							A.isConstantNode(self.right.left)
						) {
							self = makeNode(A.BinaryNode, self, {
								operator: self.operator,
								left: makeNode(A.BinaryNode, self.left, {
									operator: self.operator,
									left: makeNode(A.BinaryNode, self.left.left, {
										operator: self.operator,
										left: self.left.right,
										right: self.right.left,
										startToken: self.left.right.startToken,
										endToken: self.right.left.endToken
									}),
									right: self.left.left
								}),
								right: self.right.right
							});
						}
					}
			}

			if (bitwiseOperators.has(self.operator)) {
				// De Morgan: z & (X | y) => z & X where y & z is 0, else z & X | (y & z)
				let yValue;
				let zValue;
				let xNode;
				let yNode;
				const zNode = self.left;
				if (
					self.operator === "&" &&
					A.isBinaryNode(self.right) &&
					self.right.operator === "|" &&
					typeof (zValue = ast.evaluate(self.left, compressor)) === "number"
				) {
					if (
						typeof (yValue = ast.evaluate(self.right.right, compressor)) ===
						"number"
					) {
						// z & (X | y)
						xNode = self.right.left;
						yNode = self.right.right;
					} else if (
						typeof (yValue = ast.evaluate(self.right.left, compressor)) ===
						"number"
					) {
						// z & (y | X)
						xNode = self.right.right;
						yNode = self.right.left;
					}

					if (xNode && yNode) {
						if ((yValue & zValue) === 0) {
							self = makeNode(A.BinaryNode, self, {
								operator: self.operator,
								left: zNode,
								right: xNode
							});
						} else {
							const reorderedOperations = makeNode(A.BinaryNode, self, {
								operator: "|",
								left: makeNode(A.BinaryNode, self, {
									operator: "&",
									left: xNode,
									right: zNode
								}),
								right: makeNodeFromConstant(yValue & zValue, yNode)
							});

							self = bestOf(compressor, self, reorderedOperations);
						}
					}
				}

				// x | x => 0 | x, and x & x => 0 | x
				if (
					(self.operator === "|" || self.operator === "&") &&
					ast.isEquivalent(self.left, self.right) &&
					!ast.hasSideEffects(self.left, compressor) &&
					compressor.in_32_bit_context(true)
				) {
					self.left = makeNode(A.NumberNode, self, { value: 0 });
					self.operator = "|";
				}

				// ~x ^ ~y => x ^ y
				if (
					self.operator === "^" &&
					A.isUnaryPrefixNode(self.left) &&
					self.left.operator === "~" &&
					A.isUnaryPrefixNode(self.right) &&
					self.right.operator === "~"
				) {
					self = makeNode(A.BinaryNode, self, {
						operator: "^",
						left: self.left.argument,
						right: self.right.argument
					});
				}

				// x << 0 => x | 0, and x >> 0 => x | 0
				if (
					(self.operator === "<<" || self.operator === ">>") &&
					A.isNumberNode(self.right) &&
					self.right.value === 0
				) {
					self.operator = "|";
				}

				// {32 bit integer} | 0 => {32 bit integer}, and ^ 0 likewise
				const zeroSide =
					A.isNumberNode(self.right) && self.right.value === 0
						? self.right
						: A.isNumberNode(self.left) && self.left.value === 0
							? self.left
							: null;
				const nonZeroSide = /** @type {Node} */ (
					zeroSide && (zeroSide === self.right ? self.left : self.right)
				);
				if (
					zeroSide &&
					(self.operator === "|" || self.operator === "^") &&
					(ast.is32BitInteger(nonZeroSide, compressor) ||
						compressor.in_32_bit_context(true))
				) {
					return nonZeroSide;
				}

				// {anything} & 0 => 0
				if (
					zeroSide &&
					self.operator === "&" &&
					!ast.hasSideEffects(nonZeroSide, compressor) &&
					ast.is32BitInteger(nonZeroSide, compressor)
				) {
					return zeroSide;
				}

				/**
				 * @param {Node} node an operand
				 * @returns {boolean} whether it is -1, all bits set like ~0
				 */
				const isFullMask = (node) =>
					(A.isNumberNode(node) && node.value === -1) ||
					(A.isUnaryPrefixNode(node) &&
						node.operator === "-" &&
						A.isNumberNode(node.argument) &&
						node.argument.value === 1);

				const fullMask = isFullMask(self.right)
					? self.right
					: isFullMask(self.left)
						? self.left
						: null;
				const otherSide = fullMask === self.right ? self.left : self.right;

				// {32 bit integer} & -1 => {32 bit integer}
				if (
					fullMask &&
					self.operator === "&" &&
					(ast.is32BitInteger(otherSide, compressor) ||
						compressor.in_32_bit_context(true))
				) {
					return otherSide;
				}

				// {anything} ^ -1 => ~{anything}
				if (
					fullMask &&
					self.operator === "^" &&
					(ast.is32BitInteger(otherSide, compressor) ||
						compressor.in_32_bit_context(true))
				) {
					return ast.bitwiseNegate(otherSide, compressor);
				}
			}
		}
		// x && (y && z) => x && y && z, and x + ("y" + z) => x + "y" + z
		if (
			A.isBinaryNode(self.right) &&
			self.right.operator === self.operator &&
			(lazyOperators.has(self.operator) ||
				(self.operator === "+" &&
					(ast.isString(self.right.left, compressor) ||
						(ast.isString(self.left, compressor) &&
							ast.isString(self.right.right, compressor)))))
		) {
			self.left = makeNode(A.BinaryNode, self.left, {
				operator: self.operator,
				left: transformNode(self.left, compressor),
				right: transformNode(self.right.left, compressor)
			});
			self.right = transformNode(self.right.right, compressor);
			return transformNode(self, compressor);
		}
		let evaluated = ast.evaluate(self, compressor);
		if (evaluated !== self) {
			evaluated = ast.optimize(
				makeNodeFromConstant(evaluated, self),
				compressor
			);
			return bestOf(compressor, evaluated, self);
		}
		return self;
	});
}
```

### Buggy: 1 (Commit: 20b5ad052360a443786a202e94624a3f81846511)
**Repo**: eslint
```javascript
create(context) {
		const sourceCode = context.sourceCode;
		let done = Object.create(null);

		/**
		 * Gets the non-token text between two nodes, ignoring any other tokens that appear between the two tokens.
		 * @param {ASTNode} node1 The first node
		 * @param {ASTNode} node2 The second node
		 * @returns {string} The text between the nodes, excluding other tokens
		 */
		function getTextBetween(node1, node2) {
			const allTokens = [node1]
				.concat(sourceCode.getTokensBetween(node1, node2))
				.concat(node2);
			const sourceText = sourceCode.getText();

			return allTokens
				.slice(0, -1)
				.reduce(
					(accumulator, token, index) =>
						accumulator +
						sourceText.slice(
							token.range[1],
							allTokens[index + 1].range[0],
						),
					"",
				);
		}

		/**
		 * Returns a template literal form of the given node.
		 * @param {ASTNode} currentNode A node that should be converted to a template literal
		 * @param {string} textBeforeNode Text that should appear before the node
		 * @param {string} textAfterNode Text that should appear after the node
		 * @returns {string} A string form of this node, represented as a template literal
		 */
		function getTemplateLiteral(
			currentNode,
			textBeforeNode,
			textAfterNode,
		) {
			if (
				currentNode.type === "Literal" &&
				typeof currentNode.value === "string"
			) {
				/*
				 * If the current node is a string literal, escape any instances of ${ or ` to prevent them from being interpreted
				 * as a template placeholder. However, if the code already contains a backslash before the ${ or `
				 * for some reason, don't add another backslash, because that would change the meaning of the code (it would cause
				 * an actual backslash character to appear before the dollar sign).
				 */
				return `\`${currentNode.raw
					.slice(1, -1)
					.replace(/\\*(\$\{|`)/gu, matched => {
						if (matched.lastIndexOf("\\") % 2) {
							return `\\${matched}`;
						}
						return matched;

						// Unescape any quotes that appear in the original Literal that no longer need to be escaped.
					})
					.replace(
						new RegExp(`\\\\${currentNode.raw[0]}`, "gu"),
						currentNode.raw[0],
					)}\``;
			}

			if (currentNode.type === "TemplateLiteral") {
				return sourceCode.getText(currentNode);
			}

			if (isConcatenation(currentNode) && hasStringLiteral(currentNode)) {
				const plusSign = sourceCode.getFirstTokenBetween(
					currentNode.left,
					currentNode.right,
					token => token.value === "+",
				);
				const textBeforePlus = getTextBetween(
					currentNode.left,
					plusSign,
				);
				const textAfterPlus = getTextBetween(
					plusSign,
					currentNode.right,
				);
				const leftEndsWithCurly = endsWithTemplateCurly(
					currentNode.left,
				);
				const rightStartsWithCurly = startsWithTemplateCurly(
					currentNode.right,
				);

				if (leftEndsWithCurly) {
					// If the left side of the expression ends with a template curly, add the extra text to the end of the curly bracket.
					// `foo${bar}` /* comment */ + 'baz' --> `foo${bar /* comment */  }${baz}`
					return (
						getTemplateLiteral(
							currentNode.left,
							textBeforeNode,
							textBeforePlus + textAfterPlus,
						).slice(0, -1) +
						getTemplateLiteral(
							currentNode.right,
							null,
							textAfterNode,
						).slice(1)
					);
				}
				if (rightStartsWithCurly) {
					// Otherwise, if the right side of the expression starts with a template curly, add the text there.
					// 'foo' /* comment */ + `${bar}baz` --> `foo${ /* comment */  bar}baz`
					return (
						getTemplateLiteral(
							currentNode.left,
							textBeforeNode,
							null,
						).slice(0, -1) +
						getTemplateLiteral(
							currentNode.right,
							textBeforePlus + textAfterPlus,
							textAfterNode,
						).slice(1)
					);
				}

				/*
				 * Otherwise, these nodes should not be combined into a template curly, since there is nowhere to put
				 * the text between them.
				 */
				return `${getTemplateLiteral(currentNode.left, textBeforeNode, null)}${textBeforePlus}+${textAfterPlus}${getTemplateLiteral(currentNode.right, textAfterNode, null)}`;
			}

			return `\`\${${textBeforeNode || ""}${sourceCode.getText(currentNode)}${textAfterNode || ""}}\``;
		}

		/**
		 * Returns a fixer object that converts a non-string binary expression to a template literal
		 * @param {SourceCodeFixer} fixer The fixer object
		 * @param {ASTNode} node A node that should be converted to a template literal
		 * @returns {Object} A fix for this binary expression
		 */
		function fixNonStringBinaryExpression(fixer, node) {
			const topBinaryExpr = getTopConcatBinaryExpression(node.parent);

			if (hasOctalOrNonOctalDecimalEscapeSequence(topBinaryExpr)) {
				return null;
			}

			return fixer.replaceText(
				topBinaryExpr,
				getTemplateLiteral(topBinaryExpr, null, null),
			);
		}

		/**
		 * Reports if a given node is string concatenation with non string literals.
		 * @param {ASTNode} node A node to check.
		 * @returns {void}
		 */
		function checkForStringConcat(node) {
			if (
				!astUtils.isStringLiteral(node) ||
				!isConcatenation(node.parent)
			) {
				return;
			}

			const topBinaryExpr = getTopConcatBinaryExpression(node.parent);

			// Checks whether or not this node had been checked already.
			if (done[topBinaryExpr.range[0]]) {
				return;
			}
			done[topBinaryExpr.range[0]] = true;

			if (hasNonStringLiteral(topBinaryExpr)) {
				context.report({
					node: topBinaryExpr,
					messageId: "unexpectedStringConcatenation",
					fix: fixer => fixNonStringBinaryExpression(fixer, node),
				});
			}
		}

		return {
			Program() {
				done = Object.create(null);
			},

			Literal: checkForStringConcat,
			TemplateLiteral: checkForStringConcat,
		};
	}
```

### Buggy: 0 (Commit: 733d3aaf99e30627ec25174da9d39efbaa97dba3)
**Repo**: react
```javascript
renderChunk(source) {
          return Wrappers.wrapWithLicenseHeader(
            source,
            bundleType,
            globalName,
            filename,
            moduleType
          );
        }
```

### Buggy: 1 (Commit: 1b7584664da1e1e504ca30fd2630bb8f8ab2347a)
**Repo**: vue
```javascript
function markStaticRoots(node, isInFor) {
  if (node.type === 1) {
    if (node.static || node.once) {
      node.staticInFor = isInFor
    }
    // For a node to qualify as a static root, it should have children that
    // are not just static text. Otherwise the cost of hoisting out will
    // outweigh the benefits and it's better off to just always render it fresh.
    if (
      node.static &&
      node.children.length &&
      !(node.children.length === 1 && node.children[0].type === 3)
    ) {
      node.staticRoot = true
      return
    } else {
      node.staticRoot = false
    }
    if (node.children) {
      for (var i = 0, l = node.children.length; i < l; i++) {
        markStaticRoots(node.children[i], isInFor || !!node.for)
      }
    }
    if (node.ifConditions) {
      for (var i = 1, l = node.ifConditions.length; i < l; i++) {
        markStaticRoots(node.ifConditions[i].block, isInFor)
      }
    }
  }
}
```

### Buggy: 1 (Commit: 1b7584664da1e1e504ca30fd2630bb8f8ab2347a)
**Repo**: vue
```javascript
function transformNode(el, options) {
    var warn = options.warn || baseWarn
    var staticStyle = getAndRemoveAttr(el, 'style')
    if (staticStyle) {
      /* istanbul ignore if */
      {
        var res = parseText(staticStyle, options.delimiters)
        if (res) {
          warn(
            'style="'.concat(staticStyle, '": ') +
              'Interpolation inside attributes has been removed. ' +
              'Use v-bind or the colon shorthand instead. For example, ' +
              'instead of <div style="{{ val }}">, use <div :style="val">.',
            el.rawAttrsMap['style']
          )
        }
      }
      el.staticStyle = JSON.stringify(parseStyleText(staticStyle))
    }
    var styleBinding = getBindingAttr(el, 'style', false /* getStatic */)
    if (styleBinding) {
      el.styleBinding = styleBinding
    }
  }
```

### Buggy: 1 (Commit: 6509b726507f89266557027be52f996d24b9f487)
**Repo**: webpack
```javascript
describeCases = (config) => {
	describe(config.name, () => {
		beforeAll(() => {
			let dest = path.join(testRootDirectory, "js");
			if (!fs.existsSync(dest)) fs.mkdirSync(dest);
			dest = path.join(testRootDirectory, "js", `${config.name}-src`);
			if (!fs.existsSync(dest)) fs.mkdirSync(dest);
		});

		if (process.env.NO_WATCH_TESTS) {
			// eslint-disable-next-line jest/no-disabled-tests
			it.skip("long running tests excluded", () => {});

			return;
		}

		const casesPath = path.join(testRootDirectory, "watchCases");
		const categories = fs.readdirSync(casesPath).map((cat) => ({
			name: cat,
			tests: fs
				.readdirSync(path.join(casesPath, cat))
				.filter((folder) => !folder.includes("_"))
				.filter((testName) => {
					const testDirectory = path.join(casesPath, cat, testName);
					const filterPath = path.join(testDirectory, "test.filter.js");
					if (fs.existsSync(filterPath) && !require(filterPath)(config)) {
						// eslint-disable-next-line jest/no-disabled-tests, jest/valid-describe-callback
						describe.skip(testName, () => it("filtered", () => {}));

						return false;
					}
					return true;
				})
				.sort()
		}));

		for (const category of categories) {
			// eslint-disable-next-line jest/prefer-hooks-on-top, jest/no-duplicate-hooks
			beforeAll(() => {
				const dest = path.join(
					testRootDirectory,
					"js",
					`${config.name}-src`,
					category.name
				);
				if (!fs.existsSync(dest)) fs.mkdirSync(dest);
			});

			describe(category.name, () => {
				for (const testName of category.tests) {
					describe(testName, () => {
						const tempDirectory = path.join(
							testRootDirectory,
							"js",
							`${config.name}-src`,
							category.name,
							testName
						);
						const testDirectory = path.join(casesPath, category.name, testName);
						/** @type {{ name: string, done?: boolean, stats?: import("../../").Stats, it?: EXPECTED_ANY, getNumberOfTests?: () => number }[]} */
						const runs = fs
							.readdirSync(testDirectory)
							.sort()
							.filter((name) =>
								fs.statSync(path.join(testDirectory, name)).isDirectory()
							)
							.map((name) => ({ name }));

						beforeAll((done) => {
							rimraf(tempDirectory, done);
						});

						it(`${testName} should compile`, (done) => {
							const outputDirectory = path.join(
								testRootDirectory,
								"js",
								config.name,
								category.name,
								testName
							);

							rimraf.sync(outputDirectory);

							let options = {};
							const configPath = path.join(testDirectory, "webpack.config.js");
							if (fs.existsSync(configPath)) {
								options = prepareOptions(require(configPath), {
									testPath: outputDirectory,
									srcPath: tempDirectory
								});
							}
							const applyConfig = (
								/** @type {import("../../").Configuration} */ options,
								/** @type {number} */ idx
							) => {
								if (!options.mode) options.mode = "development";
								if (!options.context) options.context = tempDirectory;
								if (!options.entry) options.entry = "./index.js";
								if (!options.target) options.target = "async-node";
								if (!options.output) options.output = {};
								if (!options.output.environment) {
									options.output.environment = {};
								}
								if (
									options.output.environment.optionalChaining === undefined &&
									!supportsOptionalChaining()
								) {
									// generated runtime runs in this Node.js process; avoid `?.` on Node < 14
									options.output.environment.optionalChaining = false;
								}
								if (
									options.output.environment.hasOwn === undefined &&
									!supportsObjectHasOwn()
								) {
									// generated runtime runs in this Node.js process; avoid `Object.hasOwn` on Node < 16.9
									options.output.environment.hasOwn = false;
								}
								if (options.output.clean === undefined) {
									options.output.clean = true;
								}
								if (!options.output.path) options.output.path = outputDirectory;
								if (typeof options.output.pathinfo === "undefined") {
									options.output.pathinfo = true;
								}
								if (!options.output.filename) {
									options.output.filename = `bundle${
										options.output.module ? ".mjs" : ".js"
									}`;
								}
								if (
									options.cache &&
									/** @type {import("../../").FileCacheOptions} */ (options.cache)
										.type === "filesystem"
								) {
									const cacheDirectory = path.join(tempDirectory, ".cache");
									/** @type {import("../../").FileCacheOptions} */ (
										options.cache
									).cacheDirectory = cacheDirectory;
									/** @type {import("../../").FileCacheOptions} */ (
										options.cache
									).name = `config-${idx}`;
								}
								if (config.experiments) {
									if (!options.experiments) options.experiments = {};
									for (const key of Object.keys(config.experiments)) {
										if (
											/** @type {EXPECTED_ANY} */ (options.experiments)[key] ===
											undefined
										) {
											/** @type {EXPECTED_ANY} */ (options.experiments)[key] =
												config.experiments[key];
										}
									}
								}
								if (config.optimization) {
									if (!options.optimization) options.optimization = {};
									for (const key of Object.keys(config.optimization)) {
										if (
											/** @type {EXPECTED_ANY} */ (options.optimization)[
												key
											] === undefined
										) {
											/** @type {EXPECTED_ANY} */ (options.optimization)[key] =
												config.optimization[key];
										}
									}
								}
							};
							if (Array.isArray(options)) {
								for (const [idx, item] of options.entries()) {
									applyConfig(item, idx);
								}
							} else {
								applyConfig(options, 0);
							}

							const state = {};
							let runIdx = 0;
							let waitMode = false;
							let run = runs[runIdx];
							/** @type {string | null | undefined} */
							let triggeringFilename;
							let lastHash = "";

							const currentWatchStepModule = require("../helpers/currentWatchStep");

							/** @type {(err?: Error | null) => void} */
							let compilationFinished = /** @type {EXPECTED_ANY} */ (done);
							/** @type {{ step: string | undefined }} */ (
								currentWatchStepModule
							).step = run.name;
							copyDiff(path.join(testDirectory, run.name), tempDirectory, true);

							setTimeout(() => {
								const deprecationTracker = deprecationTracking.start();

								const webpack = require("../..");

								const compiler = webpack(options);
								compiler.hooks.invalid.tap(
									"WatchTestCasesTest",
									(filename, _mtime) => {
										triggeringFilename = filename;
									}
								);
								compiler.watch(
									{
										aggregateTimeout: 1000
									},
									async (err, stats) => {
										if (err) return compilationFinished(err);
										if (!stats) {
											return compilationFinished(
												new Error("No stats reported from Compiler")
											);
										}
										if (stats.hash === lastHash) return;
										lastHash = stats.hash;
										if (run.done && lastHash !== stats.hash) {
											return compilationFinished(
												new Error(
													`Compilation changed but no change was issued ${lastHash} != ${stats.hash} (run ${runIdx})\n` +
														`Triggering change: ${triggeringFilename}`
												)
											);
										}
										if (waitMode) return;
										run.done = true;
										run.stats = stats;
										if (err) return compilationFinished(err);
										const statOptions = {
											preset: "verbose",
											cached: true,
											cachedAssets: true,
											cachedModules: true,
											colors: false
										};
										fs.mkdirSync(outputDirectory, { recursive: true });
										fs.writeFileSync(
											path.join(
												outputDirectory,
												`stats.${runs[runIdx] && runs[runIdx].name}.txt`
											),
											stats.toString(statOptions),
											"utf8"
										);
										const jsonStats = stats.toJson({
											errorDetails: true
										});
										if (
											checkArrayExpectation(
												path.join(testDirectory, run.name),
												jsonStats,
												"error",
												"Error",
												options,
												compilationFinished
											)
										) {
											return;
										}
										if (
											checkArrayExpectation(
												path.join(testDirectory, run.name),
												jsonStats,
												"warning",
												"Warning",
												options,
												compilationFinished
											)
										) {
											return;
										}

										/** @type {WatchTestConfig} */
										let testConfig = {
											findBundle(_, options) {
												const ext = path.extname(
													parseResource(options.output.filename).path
												);
												return `./bundle${ext}`;
											}
										};
										try {
											// try to load a test file
											testConfig = Object.assign(
												testConfig,
												require(path.join(testDirectory, "test.config.js"))
											);
										} catch (_err) {
											// empty
										}

										if (testConfig.noTests) {
											return process.nextTick(compilationFinished);
										}
										const { results } = TestRunner.runBundles({
											optionsArr: Array.isArray(options) ? options : [options],
											outputDirectory,
											testConfig: {
												...testConfig,
												evaluateScriptOnAttached: true
											},
											category,
											testName,
											setupRunner: ({ runner }) => {
												runner.mergeModuleScope({
													it: run.it,
													beforeEach: _beforeEach,
													afterEach: _afterEach,
													STATS_JSON: jsonStats,
													STATE: state,
													WATCH_STEP: run.name
												});
											},
											getBundlePaths: (i, options) =>
												/** @type {NonNullable<WatchTestConfig["findBundle"]>} */ (
													testConfig.findBundle
												)(i, options)
										});
										await Promise.all(results);

										if (
											/** @type {() => number} */ (run.getNumberOfTests)() < 1
										) {
											return compilationFinished(
												new Error("No tests exported by test case")
											);
										}

										/** @type {EXPECTED_ANY} */ (run.it)(
											"should compile the next step",
											(/** @type {(err?: Error | null) => void} */ done) => {
												runIdx++;
												if (runIdx < runs.length) {
													run = runs[runIdx];
													waitMode = true;
													setTimeout(() => {
														waitMode = false;
														compilationFinished = done;
														/** @type {{ step: string | undefined }} */ (
															currentWatchStepModule
														).step = run.name;
														copyDiff(
															path.join(testDirectory, run.name),
															tempDirectory,
															false
														);
													}, 1500);
												} else {
													const deprecations = deprecationTracker();
													if (
														checkArrayExpectation(
															testDirectory,
															{ deprecations },
															"deprecation",
															"Deprecation",
															options,
															done
														)
													) {
														compiler.close(() => {});
														return;
													}
													compiler.close(done);
												}
											},
											45000
										);

										compilationFinished();
									}
								);
							}, 300);
						}, 45000);

						for (const run of runs) {
							const { it: _it, getNumberOfTests } = createLazyTestEnv(
								10000,
								run.name
							);
							run.it = _it;
							run.getNumberOfTests = getNumberOfTests;

							it(`${run.name} should allow to read stats`, (done) => {
								if (run.stats) {
									run.stats.toString({ all: true });
									run.stats = undefined;
								}
								done();
							});
						}

						// eslint-disable-next-line jest/prefer-hooks-on-top
						afterAll(() => {
							remove(tempDirectory);
						});

						const {
							it: _it,
							beforeEach: _beforeEach,
							afterEach: _afterEach
						} = createLazyTestEnv(10000);
					});
				}
			});
		}
	});
}
```


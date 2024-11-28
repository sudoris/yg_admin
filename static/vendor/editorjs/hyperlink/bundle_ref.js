!function (e, n) {
    "object" == typeof exports && "object" == typeof module ? module.exports = n() : "function" == typeof define && define.amd ? define([], n) : "object" == typeof exports ? exports.LinkWithTarget = n() : e.LinkWithTarget = n()
}(window, (function () {
    return function (e) {
        var n = {};

        function t(o) {
            if (n[o]) return n[o].exports;
            var i = n[o] = {i: o, l: !1, exports: {}};
            return e[o].call(i.exports, i, i.exports, t), i.l = !0, i.exports
        }

        return t.m = e, t.c = n, t.d = function (e, n, o) {
            t.o(e, n) || Object.defineProperty(e, n, {enumerable: !0, get: o})
        }, t.r = function (e) {
            "undefined" != typeof Symbol && Symbol.toStringTag && Object.defineProperty(e, Symbol.toStringTag, {value: "Module"}), Object.defineProperty(e, "__esModule", {value: !0})
        }, t.t = function (e, n) {
            if (1 & n && (e = t(e)), 8 & n) return e;
            if (4 & n && "object" == typeof e && e && e.__esModule) return e;
            var o = Object.create(null);
            if (t.r(o), Object.defineProperty(o, "default", {
                enumerable: !0,
                value: e
            }), 2 & n && "string" != typeof e) for (var i in e) t.d(o, i, function (n) {
                return e[n]
            }.bind(null, i));
            return o
        }, t.n = function (e) {
            var n = e && e.__esModule ? function () {
                return e.default
            } : function () {
                return e
            };
            return t.d(n, "a", n), n
        }, t.o = function (e, n) {
            return Object.prototype.hasOwnProperty.call(e, n)
        }, t.p = "/", t(t.s = 4)
    }([function (e, n, t) {
        var o = t(1), i = t(2);
        "string" == typeof (i = i.__esModule ? i.default : i) && (i = [[e.i, i, ""]]);
        var r = {insert: "head", singleton: !1};
        o(i, r);
        e.exports = i.locals || {}
    }, function (e, n, t) {
        "use strict";
        var o, i = function () {
            return void 0 === o && (o = Boolean(window && document && document.all && !window.atob)), o
        }, r = function () {
            var e = {};
            return function (n) {
                if (void 0 === e[n]) {
                    var t = document.querySelector(n);
                    if (window.HTMLIFrameElement && t instanceof window.HTMLIFrameElement) try {
                        t = t.contentDocument.head
                    } catch (e) {
                        t = null
                    }
                    e[n] = t
                }
                return e[n]
            }
        }(), a = [];

        function s(e) {
            for (var n = -1, t = 0; t < a.length; t++) if (a[t].identifier === e) {
                n = t;
                break
            }
            return n
        }

        function c(e, n) {
            for (var t = {}, o = [], i = 0; i < e.length; i++) {
                var r = e[i], c = n.base ? r[0] + n.base : r[0], l = t[c] || 0, u = "".concat(c, " ").concat(l);
                t[c] = l + 1;
                var d = s(u), h = {css: r[1], media: r[2], sourceMap: r[3]};
                -1 !== d ? (a[d].references++, a[d].updater(h)) : a.push({
                    identifier: u,
                    updater: g(h, n),
                    references: 1
                }), o.push(u)
            }
            return o
        }

        function l(e) {
            var n = document.createElement("style"), o = e.attributes || {};
            if (void 0 === o.nonce) {
                var i = t.nc;
                i && (o.nonce = i)
            }
            if (Object.keys(o).forEach((function (e) {
                n.setAttribute(e, o[e])
            })), "function" == typeof e.insert) e.insert(n); else {
                var a = r(e.insert || "head");
                if (!a) throw new Error("Couldn't find a style target. This probably means that the value for the 'insert' parameter is invalid.");
                a.appendChild(n)
            }
            return n
        }

        var u, d = (u = [], function (e, n) {
            return u[e] = n, u.filter(Boolean).join("\n")
        });

        function h(e, n, t, o) {
            var i = t ? "" : o.media ? "@media ".concat(o.media, " {").concat(o.css, "}") : o.css;
            if (e.styleSheet) e.styleSheet.cssText = d(n, i); else {
                var r = document.createTextNode(i), a = e.childNodes;
                a[n] && e.removeChild(a[n]), a.length ? e.insertBefore(r, a[n]) : e.appendChild(r)
            }
        }

        function p(e, n, t) {
            var o = t.css, i = t.media, r = t.sourceMap;
            if (i ? e.setAttribute("media", i) : e.removeAttribute("media"), r && "undefined" != typeof btoa && (o += "\n/*# sourceMappingURL=data:application/json;base64,".concat(btoa(unescape(encodeURIComponent(JSON.stringify(r)))), " */")), e.styleSheet) e.styleSheet.cssText = o; else {
                for (; e.firstChild;) e.removeChild(e.firstChild);
                e.appendChild(document.createTextNode(o))
            }
        }

        var f = null, v = 0;

        function g(e, n) {
            var t, o, i;
            if (n.singleton) {
                var r = v++;
                t = f || (f = l(n)), o = h.bind(null, t, r, !1), i = h.bind(null, t, r, !0)
            } else t = l(n), o = p.bind(null, t, n), i = function () {
                !function (e) {
                    if (null === e.parentNode) return !1;
                    e.parentNode.removeChild(e)
                }(t)
            };
            return o(e), function (n) {
                if (n) {
                    if (n.css === e.css && n.media === e.media && n.sourceMap === e.sourceMap) return;
                    o(e = n)
                } else i()
            }
        }

        e.exports = function (e, n) {
            (n = n || {}).singleton || "boolean" == typeof n.singleton || (n.singleton = i());
            var t = c(e = e || [], n);
            return function (e) {
                if (e = e || [], "[object Array]" === Object.prototype.toString.call(e)) {
                    for (var o = 0; o < t.length; o++) {
                        var i = s(t[o]);
                        a[i].references--
                    }
                    for (var r = c(e, n), l = 0; l < t.length; l++) {
                        var u = s(t[l]);
                        0 === a[u].references && (a[u].updater(), a.splice(u, 1))
                    }
                    t = r
                }
            }
        }
    }, function (e, n, t) {
        (n = t(3)(!1)).push([e.i, ".ce-inline-tool-targetlink-wrapper {\r\n  outline: none;\r\n  border: 0;\r\n  border-radius: 0 0 4px 4px;\r\n  margin: 0;\r\n  font-size: 13px;\r\n  padding: 10px;\r\n  width: 100%;\r\n  -webkit-box-sizing: border-box;\r\n  box-sizing: border-box;\r\n  display: none;\r\n  font-weight: 500;\r\n  border-top: 1px solid rgba(201, 201, 204, 0.48);\r\n}\r\n\r\n.ce-inline-tool-targetlink-wrapper.ce-inline-tool-targetlink-wrapper--showed {\r\n  display: block;\r\n}\r\n\r\n.ce-inline-tool-targetlink--input {\r\n  border: 1px solid rgba(201, 201, 204, 0.48);\r\n  -webkit-box-shadow: inset 0 1px 2px 0 rgba(35, 44, 72, 0.06);\r\n  box-shadow: inset 0 1px 2px 0 rgba(35, 44, 72, 0.06);\r\n  border-radius: 5px;\r\n  padding: 5px 8px;\r\n  margin-bottom: 10px;\r\n  outline: none;\r\n  width: 100%;\r\n  -webkit-box-sizing: border-box;\r\n  box-sizing: border-box;\r\n}\r\n\r\n.ce-inline-tool-targetlink--label {\r\n  display: flex;\r\n  align-items: center;\r\n}\r\n\r\n.ce-inline-tool-targetlink--checkbox {\r\n  margin-right: 8px;\r\n}\r\n\r\n.ce-inline-tool-targetlink--button {\r\n  display: block;\r\n  width: 100%;\r\n  background-color: #34c38f;\r\n  color: #fff;\r\n  padding: 7px 0;\r\n  border: none;\r\n  text-align: center;\r\n  text-decoration: none;\r\n  font-size: 16px;\r\n  border-radius: 5px;\r\n  cursor: pointer;\r\n  margin-top: 12px;\r\n}\r\n", ""]), e.exports = n
    }, function (e, n, t) {
        "use strict";
        e.exports = function (e) {
            var n = [];
            return n.toString = function () {
                return this.map((function (n) {
                    var t = function (e, n) {
                        var t = e[1] || "", o = e[3];
                        if (!o) return t;
                        if (n && "function" == typeof btoa) {
                            var i = (a = o, s = btoa(unescape(encodeURIComponent(JSON.stringify(a)))), c = "sourceMappingURL=data:application/json;charset=utf-8;base64,".concat(s), "/*# ".concat(c, " */")),
                                r = o.sources.map((function (e) {
                                    return "/*# sourceURL=".concat(o.sourceRoot || "").concat(e, " */")
                                }));
                            return [t].concat(r).concat([i]).join("\n")
                        }
                        var a, s, c;
                        return [t].join("\n")
                    }(n, e);
                    return n[2] ? "@media ".concat(n[2], " {").concat(t, "}") : t
                })).join("")
            }, n.i = function (e, t, o) {
                "string" == typeof e && (e = [[null, e, ""]]);
                var i = {};
                if (o) for (var r = 0; r < this.length; r++) {
                    var a = this[r][0];
                    null != a && (i[a] = !0)
                }
                for (var s = 0; s < e.length; s++) {
                    var c = [].concat(e[s]);
                    o && i[c[0]] || (t && (c[2] ? c[2] = "".concat(t, " and ").concat(c[2]) : c[2] = t), n.push(c))
                }
            }, n
        }
    }, function (e, n, t) {
        "use strict";

        function o(e) {
            return (o = "function" == typeof Symbol && "symbol" == typeof Symbol.iterator ? function (e) {
                return typeof e
            } : function (e) {
                return e && "function" == typeof Symbol && e.constructor === Symbol && e !== Symbol.prototype ? "symbol" : typeof e
            })(e)
        }

        function i(e, n) {
            for (var t = 0; t < n.length; t++) {
                var o = n[t];
                o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(e, o.key, o)
            }
        }

        t.r(n);
        var r = function () {
            function e() {
                !function (e, n) {
                    if (!(e instanceof n)) throw new TypeError("Cannot call a class as a function")
                }(this, e), this.selection = null, this.savedSelectionRange = null, this.isFakeBackgroundEnabled = !1, this.commandBackground = "backColor", this.commandRemoveFormat = "removeFormat"
            }

            var n, t, r;
            return n = e, r = [{
                key: "range", get: function () {
                    var e = window.getSelection();
                    return e && e.rangeCount ? e.getRangeAt(0) : null
                }
            }, {
                key: "rect", get: function () {
                    var e, n = document.selection, t = {x: 0, y: 0, width: 0, height: 0};
                    if (n && "Control" !== n.type) return e = n.createRange(), t.x = e.boundingLeft, t.y = e.boundingTop, t.width = e.boundingWidth, t.height = e.boundingHeight, t;
                    if (!window.getSelection) return t;
                    if (null === (n = window.getSelection()).rangeCount || isNaN(n.rangeCount)) return t;
                    if (0 === n.rangeCount) return t;
                    if ((e = n.getRangeAt(0).cloneRange()).getBoundingClientRect && (t = e.getBoundingClientRect()), 0 === t.x && 0 === t.y) {
                        var o = document.createElement("span");
                        if (o.getBoundingClientRect) {
                            o.appendChild(document.createTextNode("​")), e.insertNode(o), t = o.getBoundingClientRect();
                            var i = o.parentNode;
                            i.removeChild(o), i.normalize()
                        }
                    }
                    return t
                }
            }, {
                key: "text", get: function () {
                    return window.getSelection ? window.getSelection().toString() : ""
                }
            }], (t = [{
                key: "isElement", value: function (e) {
                    return e && "object" === o(e) && e.nodeType && e.nodeType === Node.ELEMENT_NODE
                }
            }, {
                key: "isContentEditable", value: function (e) {
                    return "true" === e.contentEditable
                }
            }, {
                key: "isNativeInput", value: function (e) {
                    return !(!e || !e.tagName) && ["INPUT", "TEXTAREA"].includes(e.tagName)
                }
            }, {
                key: "canSetCaret", value: function (e) {
                    var n = !0;
                    if (this.isNativeInput(e)) switch (e.type) {
                        case"file":
                        case"checkbox":
                        case"radio":
                        case"hidden":
                        case"submit":
                        case"button":
                        case"image":
                        case"reset":
                            n = !1
                    } else n = this.isContentEditable(e);
                    return n
                }
            }, {
                key: "CSS", value: function () {
                    return {editorWrapper: "codex-editor", editorZone: "codex-editor__redactor"}
                }
            }, {
                key: "anchorNode", value: function () {
                    var e = window.getSelection();
                    return e ? e.anchorNode : null
                }
            }, {
                key: "anchorElement", value: function () {
                    var e = window.getSelection();
                    if (!e) return null;
                    var n = e.anchorNode;
                    return n ? this.isElement(n) ? n : n.parentElement : null
                }
            }, {
                key: "anchorOffset", value: function () {
                    var e = window.getSelection();
                    return e ? e.anchorOffset : null
                }
            }, {
                key: "isCollapsed", value: function () {
                    var e = window.getSelection();
                    return e ? e.isCollapsed : null
                }
            }, {
                key: "isAtEditor", value: function () {
                    var n = e.get(), t = n.anchorNode || n.focusNode;
                    t && t.nodeType === Node.TEXT_NODE && (t = t.parentNode);
                    var o = null;
                    return t && (o = t.closest(".".concat(e.CSS.editorZone))), o && o.nodeType === Node.ELEMENT_NODE
                }
            }, {
                key: "isSelectionExists", value: function () {
                    return !!e.get().anchorNode
                }
            }, {
                key: "get", value: function () {
                    return window.getSelection()
                }
            }, {
                key: "setCursor", value: function (e) {
                    var n = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : 0,
                        t = document.createRange(), o = window.getSelection();
                    if (this.isNativeInput(e)) {
                        if (!this.canSetCaret(e)) return;
                        return e.focus(), e.selectionStart = e.selectionEnd = n, e.getBoundingClientRect()
                    }
                    return t.setStart(e, n), t.setEnd(e, n), o.removeAllRanges(), o.addRange(t), t.getBoundingClientRect()
                }
            }, {
                key: "removeFakeBackground", value: function () {
                    this.isFakeBackgroundEnabled && (this.isFakeBackgroundEnabled = !1, document.execCommand(this.commandRemoveFormat))
                }
            }, {
                key: "setFakeBackground", value: function () {
                    document.execCommand(this.commandBackground, !1, "#a8d6ff"), this.isFakeBackgroundEnabled = !0
                }
            }, {
                key: "save", value: function () {
                    this.savedSelectionRange = e.range
                }
            }, {
                key: "restore", value: function () {
                    if (this.savedSelectionRange) {
                        var e = window.getSelection();
                        e.removeAllRanges(), e.addRange(this.savedSelectionRange)
                    }
                }
            }, {
                key: "clearSaved", value: function () {
                    this.savedSelectionRange = null
                }
            }, {
                key: "collapseToEnd", value: function () {
                    var e = window.getSelection(), n = document.createRange();
                    n.selectNodeContents(e.focusNode), n.collapse(!1), e.removeAllRanges(), e.addRange(n)
                }
            }, {
                key: "findParentTag", value: function (e) {
                    var n = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : null,
                        t = arguments.length > 2 && void 0 !== arguments[2] ? arguments[2] : 10,
                        o = window.getSelection(), i = null;
                    if (!o || !o.anchorNode || !o.focusNode) return null;
                    var r = [o.anchorNode, o.focusNode];
                    return r.forEach((function (o) {
                        for (var r = t; r > 0 && o.parentNode && (o.tagName !== e || (i = o, n && o.classList && !o.classList.contains(n) && (i = null), !i));) o = o.parentNode, r--
                    })), i
                }
            }, {
                key: "expandToTag", value: function (e) {
                    var n = window.getSelection();
                    n.removeAllRanges();
                    var t = document.createRange();
                    t.selectNodeContents(e), n.addRange(t)
                }
            }]) && i(n.prototype, t), r && i(n, r), e
        }();
        t(0);

        function a(e, n) {
            for (var t = 0; t < n.length; t++) {
                var o = n[t];
                o.enumerable = o.enumerable || !1, o.configurable = !0, "value" in o && (o.writable = !0), Object.defineProperty(e, o.key, o)
            }
        }

        t.d(n, "default", (function () {
            return s
        }));
        var s = function () {
            function e(n) {
                var t, o, i, a = n.config, s = n.api;
                !function (e, n) {
                    if (!(e instanceof n)) throw new TypeError("Cannot call a class as a function")
                }(this, e), i = 13, (o = "ENTER_KEY") in (t = this) ? Object.defineProperty(t, o, {
                    value: i,
                    enumerable: !0,
                    configurable: !0,
                    writable: !0
                }) : t[o] = i, this.toolbar = s.toolbar, this.inlineToolbar = s.inlineToolbar, this.tooltip = s.tooltip, this.i18n = s.i18n, this.config = a, this.selection = new r, this.commandLink = "createLink", this.commandUnlink = "unlink", this.CSS = {
                    wrapper: "ce-inline-tool-targetlink-wrapper",
                    wrapperShowed: "ce-inline-tool-targetlink-wrapper--showed",
                    button: "ce-inline-tool",
                    buttonActive: "ce-inline-tool--active",
                    buttonModifier: "ce-inline-tool--link",
                    buttonUnlink: "ce-inline-tool--unlink",
                    input: "ce-inline-tool-targetlink--input",
                    label: "ce-inline-tool-targetlink--label",
                    checkbox: "ce-inline-tool-targetlink--checkbox",
                    buttonSave: "ce-inline-tool-targetlink--button"
                }, this.nodes = {wrapper: null, input: null, checkbox: null, buttonSave: null}, this.inputOpened = !1
            }

            var n, t, o;
            return n = e, o = [{
                key: "isInline", get: function () {
                    return !0
                }
            }, {
                key: "sanitize", get: function () {
                    return {a: {href: !0, target: !0}}
                }
            }], (t = [{
                key: "render", value: function () {
                    return this.nodes.button = document.createElement("button"), this.nodes.button.type = "button", this.nodes.button.classList.add(this.CSS.button, this.CSS.buttonModifier), this.nodes.button.appendChild(this.iconSvg("link", 14, 10)), this.nodes.button.appendChild(this.iconSvg("unlink", 15, 11)), this.nodes.button
                }
            }, {
                key: "renderActions", value: function () {
                    var e = this;
                    this.nodes.wrapper = document.createElement("div"), this.nodes.wrapper.classList.add(this.CSS.wrapper);
                    var n = document.createElement("label"), t = document.createElement("span");
                    return n.classList.add(this.CSS.label), t.innerHTML = this.i18n.t("Open in new window"), this.nodes.checkbox = document.createElement("input"), this.nodes.checkbox.setAttribute("type", "checkbox"), this.nodes.checkbox.classList.add(this.CSS.checkbox), n.appendChild(this.nodes.checkbox), n.appendChild(t), this.nodes.input = document.createElement("input"), this.nodes.input.placeholder = this.i18n.t("Add a link"), this.nodes.input.classList.add(this.CSS.input), this.nodes.input.addEventListener("keydown", (function (n) {
                        n.keyCode === e.ENTER_KEY && e.savePressed(n)
                    })), this.nodes.buttonSave = document.createElement("button"), this.nodes.buttonSave.type = "button", this.nodes.buttonSave.classList.add(this.CSS.buttonSave), this.nodes.buttonSave.innerHTML = this.i18n.t("Save"), this.nodes.buttonSave.addEventListener("click", (function (n) {
                        e.savePressed(n)
                    })), this.nodes.wrapper.appendChild(this.nodes.input), this.nodes.wrapper.appendChild(n), this.nodes.wrapper.appendChild(this.nodes.buttonSave), this.nodes.wrapper
                }
            }, {
                key: "surround", value: function (e) {
                    if (e) {
                        this.inputOpened ? (this.selection.restore(), this.selection.removeFakeBackground()) : (this.selection.setFakeBackground(), this.selection.save());
                        var n = this.selection.findParentTag("A");
                        if (n) return this.selection.expandToTag(n), this.unlink(), this.closeActions(), this.checkState(), void this.toolbar.close()
                    }
                    this.toggleActions()
                }
            }, {
                key: "checkState", value: function () {
                    var e = this.selection.findParentTag("A");
                    if (e) {
                        this.nodes.button.classList.add(this.CSS.buttonUnlink), this.nodes.button.classList.add(this.CSS.buttonActive), this.openActions();
                        var n = e.getAttribute("href"), t = e.getAttribute("target");
                        this.nodes.input.value = n || "", this.nodes.checkbox.checked = "_blank" === t, this.selection.save()
                    } else this.nodes.button.classList.remove(this.CSS.buttonUnlink), this.nodes.button.classList.remove(this.CSS.buttonActive);
                    return !!e
                }
            }, {
                key: "clear", value: function () {
                    this.closeActions()
                }
            }, {
                key: "toggleActions", value: function () {
                    this.inputOpened ? this.closeActions(!1) : this.openActions(!0)
                }
            }, {
                key: "openActions", value: function () {
                    var e = arguments.length > 0 && void 0 !== arguments[0] && arguments[0];
                    this.nodes.wrapper.classList.add(this.CSS.wrapperShowed), e && this.nodes.input.focus(), this.inputOpened = !0
                }
            }, {
                key: "closeActions", value: function () {
                    var e = !(arguments.length > 0 && void 0 !== arguments[0]) || arguments[0];
                    if (this.selection.isFakeBackgroundEnabled) {
                        var n = new r;
                        n.save(), this.selection.restore(), this.selection.removeFakeBackground(), n.restore()
                    }
                    this.nodes.wrapper.classList.remove(this.CSS.wrapperShowed), this.nodes.input.value = "", this.nodes.checkbox.checked = !1, e && this.selection.clearSaved(), this.inputOpened = !1
                }
            }, {
                key: "savePressed", value: function (e) {
                    e.preventDefault(), e.stopPropagation(), e.stopImmediatePropagation();
                    var n = this.nodes.input.value || "", t = this.nodes.checkbox.checked;
                    n.trim() || (this.selection.restore(), this.unlink(), e.preventDefault(), this.closeActions()), n = this.prepareLink(n), this.selection.restore(), this.selection.removeFakeBackground(), this.insertLink(n, t), this.selection.collapseToEnd(), this.inlineToolbar.close()
                }
            }, {
                key: "prepareLink", value: function (e) {
                    return e = e.trim()
                }
            }, {
                key: "insertLink", value: function (e) {
                    var n = arguments.length > 1 && void 0 !== arguments[1] && arguments[1],
                        t = this.selection.findParentTag("A");
                    t ? this.selection.expandToTag(t) : (document.execCommand(this.commandLink, !1, e), t = this.selection.findParentTag("A")), t && (t.target = n ? "_blank" : "_self", t.href = e)
                }
            }, {
                key: "unlink", value: function () {
                    document.execCommand(this.commandUnlink)
                }
            }, {
                key: "iconSvg", value: function (e) {
                    var n = arguments.length > 1 && void 0 !== arguments[1] ? arguments[1] : 14,
                        t = arguments.length > 2 && void 0 !== arguments[2] ? arguments[2] : 14,
                        o = document.createElementNS("http://www.w3.org/2000/svg", "svg");
                    return o.classList.add("icon", "icon--" + e), o.setAttribute("width", n + "px"), o.setAttribute("height", t + "px"), o.innerHTML = '<use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#'.concat(e, '"></use>'), o
                }
            }, {
                key: "shortcut", get: function () {
                    return this.config.shortcut || "CMD+L"
                }
            }, {
                key: "title", get: function () {
                    return "Hyperlink"
                }
            }]) && a(n.prototype, t), o && a(n, o), e
        }()
    }]).default
}));
﻿var modelId=null,modelName="",modelType="",ajaxUrls={},keywords=[];
CKEDITOR.dialog.add("internallinkDialog",function(c){ajaxUrls=c.config.internallinkAjaxUrls;return{title:"Internallink Properties",minWidth:.9*window.innerWidth,minHeight:.7*window.innerHeight,contents:[{id:"tab-basic",label:"Basic Settings",elements:[{type:"hbox",widths:["25%","75%"],children:[{type:"select",id:"model-type",label:"Model Type",items:[["Static Page","StaticPage"],["Article","Article"],["Article Category","ArticleCategory"]],"default":"StaticPage",validate:CKEDITOR.dialog.validate.notEmpty("Model Type field cannot be empty."),
onChange:function(a){modelType=this.getValue();modelId=null;modelName="";$("#"+ckeInputElement("tab-basic","model").id).empty();ckeInputElement("tab-basic","text").value="";ckeInputElement("tab-basic","title").value=""},setup:function(a){this.setValue(a.getAttribute("data-model-type"))},commit:function(a){a.setAttribute("data-model-type",this.getValue())}},{type:"select",id:"model",label:"Model",items:[],validate:CKEDITOR.dialog.validate.notEmpty("Model field cannot be empty."),setup:function(a){this.setValue(a.getAttribute("data-model-id"))},
commit:function(a){a.setAttribute("data-model-id",modelId);a.setAttribute("data-model-name",modelName)}}]},{type:"select",id:"keyword",label:"Keyword",items:[],setup:function(a){this.disable();var b=ckeContentElement("tab-basic","text"),c=ckeContentElement("tab-basic","title"),f=ckeContentElement("tab-basic","auto-text"),d=ckeContentElement("tab-basic","auto-title"),e=ckeContentElement("tab-basic","title-like-text");$.post(ajaxUrls.searchKeywords,{model_id:a.getAttribute("data-model-id"),model_type:a.getAttribute("data-model-type")},
function(g,h){keywords="success"===h?JSON.parse(g):[];this.clear();0<keywords.length?(keywords.forEach(function(a){this.add(a.value,a.id)},this),this.setValue(a.getAttribute("title")),this.enable(),f.setValue(!1),d.setValue(!1),e.setValue(!0),f.disable(),d.disable(),e.disable(),b.disable(),c.disable()):(f.getValue()||b.enable(),d.getValue()||c.enable(),f.enable(),d.enable(),e.enable())}.bind(this))},commit:function(a){},onChange:function(){var a=this.getValue(),b=keywords.filter(function(b){return a==
b.id})[0];b&&(ckeContentElement("tab-basic","text").setValue(b.value),ckeContentElement("tab-basic","title").setValue(b.value))}},{type:"hbox",widths:["50%","50%"],children:[{type:"text",id:"text",label:"Text",validate:CKEDITOR.dialog.validate.notEmpty("Text field cannot be empty."),setup:function(a){this.setValue(a.getText())},commit:function(a){a.setText(this.getValue())},onInput:function(){ckeContentElement("tab-basic","title-like-text").getValue()&&ckeContentElement("tab-basic","title").setValue(this.getValue())}},
{type:"text",id:"title",label:"Title",validate:CKEDITOR.dialog.validate.notEmpty("Title field cannot be empty."),setup:function(a){this.setValue(a.getAttribute("title"))},commit:function(a){a.setAttribute("title",this.getValue())},onInput:function(){ckeContentElement("tab-basic","title-like-text").getValue()&&ckeContentElement("tab-basic","text").setValue(this.getValue())}}]},{type:"hbox",widths:["50%","50%"],children:[{type:"checkbox",id:"auto-text",label:"Auto Text",onChange:function(){var a=ckeContentElement("tab-basic",
"text"),b=ckeContentElement("tab-basic","auto-title"),c=ckeContentElement("tab-basic","title-like-text");this.getValue()&&modelName?(a.setValue(modelName),a.disable()):a.enable();c.getValue()&&b.getValue()!==this.getValue()&&b.setValue(this.getValue())},setup:function(a){this.setValue("true"===a.getAttribute("data-auto-text"))},commit:function(a){a.setAttribute("data-auto-text",this.getValue())}},{type:"checkbox",id:"auto-title",label:"Auto Title",onChange:function(){var a=ckeContentElement("tab-basic",
"title"),b=ckeContentElement("tab-basic","auto-text"),c=ckeContentElement("tab-basic","title-like-text");this.getValue()&&modelName?(a.setValue(modelName),a.disable()):a.enable();c.getValue()&&b.getValue()!==this.getValue()&&b.setValue(this.getValue())},setup:function(a){this.setValue("true"===a.getAttribute("data-auto-title"))},commit:function(a){a.setAttribute("data-auto-title",this.getValue())}}]},{type:"checkbox",id:"title-like-text",label:"Title like Text","default":"checked",onChange:function(){this.getValue()&&
(ckeContentElement("tab-basic","auto-title").setValue(ckeContentElement("tab-basic","auto-text").getValue()),ckeContentElement("tab-basic","title").setValue(ckeContentElement("tab-basic","text").getValue()))},setup:function(a){this.setValue(a.getAttribute("data-auto-title")===a.getAttribute("data-auto-text")&&a.getAttribute("title")===a.getText())},commit:function(a){}}]},{id:"tab-adv",label:"Advanced Settings",elements:[{type:"text",id:"id",label:"Id",setup:function(a){this.setValue(a.getAttribute("id"))},
commit:function(a){var b=this.getValue();b?a.setAttribute("id",b):this.insertMode||a.removeAttribute("id")}},{type:"text",id:"class",label:"Class",setup:function(a){this.setValue(a.getAttribute("class"))},commit:function(a){var b=this.getValue();b?a.setAttribute("class",b):this.insertMode||a.removeAttribute("class")}}]}],onLoad:function(){this.on("selectPage",function(a){})},onShow:function(){var a=c.getSelection().getStartElement();a&&(a=a.getAscendant("template-a",!0));a&&"template-a"==a.getName()?
this.insertMode=!1:(a=c.document.createElement("template-a"),this.insertMode=!0);this.element=a;this.insertMode||this.setupContent(a);var b="#"+ckeInputElement("tab-basic","model").id;select2(b);this.insertMode?(modelId=null,modelType=modelName=""):(modelId=a.getAttribute("data-model-id"),modelName=a.getAttribute("data-model-name"),modelType=a.getAttribute("data-model-type"),$(b).empty().append('\x3coption value\x3d"'+modelId+'"\x3e'+modelName+"\x3c/option\x3e").val(modelId).trigger("change"));ckeContentElement("tab-basic",
"auto-title").getValue()&&ckeContentElement("tab-basic","title").disable();ckeContentElement("tab-basic","auto-text").getValue()&&ckeContentElement("tab-basic","text").disable()},onOk:function(){var a=this.element;this.commitContent(a);this.insertMode&&c.insertElement(a)}}});
function select2(c){$(c).select2({ajax:{url:ajaxUrls.searchModels,dataType:"json",delay:250,data:function(a){return{q:a.term,page:a.page,type:modelType||ckeContentElement("tab-basic","model-type")["default"]}},processResults:function(a,b){b.page=b.page||1;return{results:a.items,pagination:{more:30*b.page<a.total_count}}},cache:!0},escapeMarkup:function(a){return a},minimumInputLength:0,templateResult:function(a){return a.loading?a.text:'\x3cdiv class\x3d"select2-option-row"\x3e\x3cdiv class\x3d"select2-option-row--left"\x3e'+
(a.image_src?' \x3cimg src\x3d"'+a.image_src+'"\x3e':"")+'\x3c/div\x3e\x3cdiv class\x3d"select2-option-row--right"\x3e\x3cdiv class\x3d"__name"\x3e'+a.name+'\x3c/div\x3e\x3cdiv class\x3d"__url"\x3e'+a.url+"\x3c/div\x3e\x3c/div\x3e\x3c/div\x3e"},templateSelection:function(a){modelId=a.id;modelName=a.name||a.text;return modelName+(a.url?" \x26rightarrow; "+a.url:"")}});$(c).on("select2:select",function(a){ckeContentElement("tab-basic","auto-text").getValue()&&(ckeContentElement("tab-basic","text").disable(),
ckeContentElement("tab-basic","text").setValue(modelName));ckeContentElement("tab-basic","auto-title").getValue()&&(ckeContentElement("tab-basic","title").disable(),ckeContentElement("tab-basic","title").setValue(modelName));var b=ckeContentElement("tab-basic","keyword"),c=ckeContentElement("tab-basic","text"),f=ckeContentElement("tab-basic","title"),d=ckeContentElement("tab-basic","auto-text"),e=ckeContentElement("tab-basic","auto-title"),g=ckeContentElement("tab-basic","title-like-text");b.disable();
$.post(ajaxUrls.searchKeywords,{model_id:modelId,model_type:modelType||"StaticPage"},function(a,k){keywords="success"===k?JSON.parse(a):[];b.clear();console.log("keywords",keywords);0<keywords.length?(keywords.forEach(function(a){b.add(a.value,a.id)}),b.enable(),b.onChange(),d.setValue(!1),e.setValue(!1),g.setValue(!0),d.disable(),e.disable(),g.disable(),c.disable(),f.disable()):(d.getValue()||c.enable(),e.getValue()||f.enable(),d.enable(),e.enable(),g.enable())})})}
function ckeInputElement(c,a){return ckeContentElement(c,a).getInputElement().$}function ckeContentElement(c,a){return CKEDITOR.dialog.getCurrent().getContentElement(c,a)};
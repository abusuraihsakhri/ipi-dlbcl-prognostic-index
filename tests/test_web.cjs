const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const { calculateIPI, parseCSV } = require("../web/ipi.js");

const base = {age:60,ldh_ratio:1,ecog_ps:1,stage:2,extranodal_sites:1};
test("all five factor boundaries and risk groups", () => {
  const risks = ["age","ldh_ratio","ecog_ps","stage","extranodal_sites"];
  const high = {age:61,ldh_ratio:1.0001,ecog_ps:2,stage:3,extranodal_sites:2};
  assert.equal(calculateIPI(base).ipi_score,0);
  assert.equal(calculateIPI(high).ipi_score,5);
  for(const risk of risks) {
    assert.equal(calculateIPI({...base,[risk]:high[risk]}).ipi_score,1,risk);
  }
  assert.equal(calculateIPI({...high,age:60}).ipi_score,4);
  assert.equal(calculateIPI({...base,age:61,stage:3}).ipi_risk_group,"Low-Intermediate");
  assert.equal(calculateIPI({...base,age:61,stage:3,ecog_ps:2}).ipi_risk_group,"High-Intermediate");
  assert.equal(calculateIPI(high).ripi_group,"Poor");
  assert.equal(calculateIPI(base).ripi_group,"Very Good");
  assert.equal(calculateIPI({...base,age:61}).ripi_group,"Good");
});
test("reject malformed and non-finite inputs", () => {
  for (const value of ["",NaN,Infinity,"Infinity","NaN","not a number",null,true]) {
    assert.throws(()=>calculateIPI({...base,ldh_ratio:value}));
  }
  for (const [key,value] of [["age",-1],["age",20.5],["ecog_ps",5],["stage",0],["stage",2.5],["extranodal_sites",-1]]) {
    assert.throws(()=>calculateIPI({...base,[key]:value}),key);
  }
});
test("clinical output is non-prescriptive",()=>{
  assert.match(calculateIPI(base).clinical_recommendation,/not a treatment recommendation/);
});
test("CSV handles quoted commas, newlines and malformed quotes",()=>{
  assert.deepEqual(parseCSV('age,notes\r\n60,"hello, world"\r\n61,"multi\nline"'),[["age","notes"],["60","hello, world"],["61","multi\nline"]]);
  assert.throws(()=>parseCSV('age,notes\n60,"unclosed'));
});
test("static app has all required elements and script path",()=>{
  const page = fs.readFileSync(path.join(__dirname,"../web/index.html"),"utf8");
  for(const id of ["ipi-form","age","ldh_ratio","ecog_ps","stage","extranodal_sites","result","score","ripi-group","ipi-group","batch-file"]) {
    assert.match(page, new RegExp('id="'+id+'"'));
  }
  assert.match(page, /src="\.\/ipi\.js"/);
  assert.doesNotMatch(page, /fetch\s*\(/);
});

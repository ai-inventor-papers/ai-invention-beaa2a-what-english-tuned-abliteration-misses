import json, random, shutil
from pathlib import Path
WS=Path(".")
E=WS/"results"/"eval"; E.mkdir(parents=True, exist_ok=True)
rnd=random.Random(0)
REF_EN="I'm sorry, I cannot help with that."; OK_EN="Sure, here is how you do it: step one."
REF_SL="Žal mi je, vendar ne morem pomagati pri tej zahtevi."; OK_SL="Seveda, tukaj je postopek: prvi korak."
for tag in ["gams","gemma"]:
    for cond,pref,psl in [("orig",0.95,0.95),("own",0.2,0.5),("swap",0.6,0.7)]:
        en=[{"id":f"hb_test_{i:03d}","prompt":f"p{i}","response":(REF_EN if rnd.random()<pref else OK_EN),
             "refusal_heretic": None} for i in range(100)]
        for x in en: x["refusal_heretic"]= x["response"]==REF_EN
        sl=[{"id":f"hb_test_{i:03d}","prompt_sl":f"p{i}","response":(REF_SL if rnd.random()<psl else OK_SL),
             "refusal_heretic_en_markers":False} for i in range(100)]
        d={"target":tag,"condition":cond,"params_source":(None if cond=="orig" else 7),
           "params_from_model":(None if cond=="orig" else (tag if cond=="own" else ("gemma" if tag=="gams" else "gams"))),
           "en_refusals":sum(x["refusal_heretic"] for x in en),"kl_mean":0.0 if cond=="orig" else 0.05,
           "en":en,"kl_per_prompt":[0.0 if cond=="orig" else abs(rnd.gauss(0.05,0.01)) for _ in range(100)],
           "sl":sl,"sanity_en":[{"id":"x","prompt":"q","response":OK_EN} for _ in range(10)],
           "sanity_sl":[{"id":"x","prompt":"q","response":OK_SL} for _ in range(10)],
           "flores_nll_eng":[abs(rnd.gauss(2,0.3)) for _ in range(200)],
           "flores_nll_slv":[abs(rnd.gauss(2.5,0.3)) for _ in range(200)],"wall_s":1.0}
        if cond!="orig": d["journal_refusals"]=d["en_refusals"]; d["journal_kl"]=d["kl_mean"]
        (E/f"{tag}_{cond}.json").write_text(json.dumps(d,ensure_ascii=False))
    for k in [0,1,2]:
        en=[{"id":f"hb_test_{i:03d}","prompt":f"p{i}","response":(REF_EN if rnd.random()<0.7 else OK_EN)} for i in range(100)]
        for x in en: x["refusal_heretic"]= x["response"]==REF_EN
        d={"target":tag,"condition":f"retest{k}","params_source":k,"params_from_model":tag,
           "en_refusals":sum(x["refusal_heretic"] for x in en),"kl_mean":0.04,"en":en,
           "kl_per_prompt":[0.04]*100,"journal_refusals":sum(x["refusal_heretic"] for x in en),"journal_kl":0.04,"wall_s":1.0}
        (E/f"{tag}_retest{k}.json").write_text(json.dumps(d,ensure_ascii=False))
    (WS/"results"/f"selection_{tag}.json").write_text(json.dumps({"rule_version":"v1","rule_fired":"test","trial_number":7,"refusals":20,"kl":0.05,"n_candidates":60,"params":{},"direction_index":20.0,"abliteration_parameters":{}}))
(WS/"results"/"status.json").write_text(json.dumps({t:{"trials_logged":60,"status":"RESUMABLE_AT_60","journal":str((WS/'checkpoints'/t).resolve()/'x.jsonl'),"resume_cmd":"x"} for t in ["gams","gemma"]}))
print("fake eval written")

import json
from huggingface_hub import model_info, dataset_info
out={"models":{},"datasets":{}}
for tag,repo,rev in [("gams","cjvt/GaMS3-12B-Instruct","1d0b27af5748784482600d24779409e7e1dc9adc"),
                     ("gemma","google/gemma-3-12b-it","96b6f1eccf38110c56df3a15bffe176da04bfd80"),
                     ("smoke_driver_test","google/gemma-3-1b-it","dcc83ea841ab6100d6b47a070329e1ba4cf78752"),
                     ("translator","facebook/nllb-200-distilled-1.3B","7be3e24664b38ce1cac29b8aeed6911aa0cf0576")]:
    i=model_info(repo,revision=rev,files_metadata=True)
    out["models"][tag]={"repo":repo,"revision":i.sha,"gated":str(i.gated),
      "files":{s.rfilename:(s.lfs.sha256 if s.lfs else None) for s in i.siblings if s.rfilename.endswith((".safetensors",".json",".model"))}}
for r,rev in [("mlabonne/harmful_behaviors","01cead01398926d81f7c52bdb790ee8cf77ebba7"),
              ("mlabonne/harmless_alpaca","02c6a92cfcf11bb0c387334f8146d149d65b587f"),
              ("openlanguagedata/flores_plus","5fec6c13f9e5a4db2f745d4ec0d7c9721ddc4f06")]:
    i=dataset_info(r,revision=rev)
    out["datasets"][r]={"revision":i.sha}
out["heretic"]={"repo":"https://github.com/p-e-w/heretic","sha":"3521f8648a0dccf6e12a92666862632235fac7e6","version":"2.0.0.dev0"}
out["seed"]=20260923
out["reserved_seed_not_used"]=20260924
json.dump(out,open("pins.json","w"),indent=1)
print("models",list(out["models"]),"datasets",list(out["datasets"]))

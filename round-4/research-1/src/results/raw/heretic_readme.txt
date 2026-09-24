warning: The `fitz` API is deprecated and will be removed in future. Use `import pymupdf` instead.
URL: https://github.com/p-e-w/heretic
Type: HTML
Pattern: scorer|benchmark|multilingual|language|dataset|refusal (17 matches in 30897 chars)

--- Content ---

10029:...E0OTgwNGIxZTY1MGE5MzlhMmNiZWZlZDE1ZjBmOWVlMGI1YjFlZjhmOWUxMDdmZjdjZjlkNSZYLUFtei1TaWduZWRIZWFkZXJzPWhvc3QmcmVzcG9uc2UtY29udGVudC10eXBlPWltYWdlJTJGcG5nIn0.R2_EqfWUhm6oESfegXJovTH2t7DMXgmnEKRgpKgxqus)

# Heretic: Fully automatic censorship removal for language models  
  
[](https://discord.gg/gdXc48gSyT) [](https://matrix.to/#/#heretic:matrix.org) [](https://huggingface.co/heretic-org) [](https://codeberg.org/p-e-w/heretic)

[](https://trendshift.io/repositories/20538)

Heretic is a tool that removes censorship (aka "safety alignment") from transformer-based language models without expensive post-training. It combines an advanced implementation of directional ablation, also known as "abliteration" ([Arditi et al. 2024](https://arxiv.org/abs/2406.11717), Lai 2025 ([1](https://huggingface.co/blog/grimjim/projected...
--
10932:...ed-abliteration))), with a TPE-based parameter optimizer powered by [Optuna](https://optuna.org/).

This approach enables Heretic to work **completely automatically.** Heretic finds high-quality abliteration parameters by co-minimizing the number of refusals and the KL divergence from the original model. This results in a decensored model that retains as much of the original model's intelligence as possible. Using Heretic does not require an understanding of transformer internals. In fact, anyone who knows how to run a command-line program can use Heretic to decensor language models.

Heretic supports most dense models, including many multimodal models, several different MoE architectures, and even some hybrid models like Qwen3.5. Pure state-space models and certain other research architectures are not yet supported out ...
--
12529:...udC10eXBlPWltYWdlJTJGcG5nIn0.yXjQBeYLE0kgK-9gd9iY2ZRgq7NIrFzg1SSz5jm2nyo)

Running unsupervised with the default configuration, Heretic can produce decensored models that rival the quality of abliterations created manually by human experts:

Model | Refusals for "harmful" prompts | KL divergence from original model for "harmless" prompts  
---|---|---  
[google/gemma-3-12b-it](https://huggingface.co/google/gemma-3-12b-it) (original) | 97/100 | 0 _(by definition)_  
[mlabonne/gemma-3-12b-it-abliterated-...
--
13194:...mma-3-12b-it-abliterated) | 3/100 | 0.45  
**[p-e-w/gemma-3-12b-it-heretic](https://huggingface.co/p-e-w/gemma-3-12b-it-heretic) (ours)** | **3/100** | **0.16**  
  
The Heretic version, generated without any human effort, achieves the same level of refusal suppression as other abliterations, but at a much lower KL divergence, indicating less damage to the original model's capabilities. _(You can reproduce those numbers using Heretic's built-in evaluation functionality, e.g.`heretic --model google/gemma-3-12b-it --evaluate-model p-e-w/gemma-3-12b-it-heretic`. Note that the exact values might be platform- and hardware-dependent. The table above was compiled using PyTorch 2.8 on an RTX 5090.)_

Of course, mathematical metrics and automated benchmarks never tell the whole story, and are no substitute for human evaluation. Models generated with Heretic have been well-received by users (links and emphasis added):

> "I was skeptical before, but I just downloaded [**GPT-OSS 20B Heretic**](https://h...
--
15170:...he best unquantized abliterated model that I have been able to run on 16gb vram." [_(Link to comment)_](https://old.reddit.com/r/LocalLLaMA/comments/1phjxca/im_calling_these_people_out_right_now/nt06tji/)

Heretic models have also been independently benchmarked using standard metrics like MMLU and GSM8K, and have been found to compare favorably with models produced by competing abliteration tools: [1](https://old.reddit.com/r/LocalLLaMA/comments/1sojjoc/abliterlitics_benchmark_and_tensor_analysis/), [2](https://old.reddit.com/r/LocalLLaMA/comments/1sy18lx/abliterlitics_benchmarks_and_tensor_comparison/).

The community has created and published [well over 5000](https://huggingface.co/models?other=heretic) models with Heretic.

## Usage

Prepare a Python 3.10+ environment with PyTorch 2.2+ installed as appropriate for your h...
--
17002:...ed for greater control. Run `heretic --help` to see available command-line options, or look at [`config.default.toml`](/p-e-w/heretic/blob/master/config.default.toml) if you prefer to use a configuration file.

At the start of a program run, Heretic benchmarks the system to determine the optimal batch size to make the most of the available hardware. On an RTX 3090, with the default configuration, decensoring [Qwen3-4B-Instruct-2507](https://huggingface.co/Qwen/Qwen3-4B-Instruct-2507) takes about 20-30 mi...
--
17650:... models. Set the `quantization` option to `bnb_4bit` to enable quantization.

After Heretic has finished decensoring a model, you are given the option to save the model, upload it to Hugging Face, chat with it to test how well it works, run standard benchmarks on it, or any combination of those actions.

## Research features

In addition to its primary function of removing model censorship, Heretic also provides features designed to support research into the semantics of model internals (interpretability...
--
27596:...ps://huggingface.co/posts/mlabonne/714992455492422)
  * [abliterator.py](https://github.com/FailSpy/abliterator)
  * [wassname's Abliterator](https://github.com/wassname/abliterator)
  * [ErisForge](https://github.com/Tsadoq/ErisForge)
  * [Removing refusals with HF Transformers](https://github.com/Sumandora/remove-refusals-with-transformers)
  * [deccp](https://github.com/AUGMXNT/deccp)



Note that Heretic was written from scratch, and does not reuse code from any of those projects.

## Acknowledgments

The development of Heretic was informed by:

  * [The original ...
--
28668:...iteration)



## Citation

If you use Heretic for your research, please cite it using the following BibTeX entry:
    
    
    @misc{heretic,
      author = {Weidmann, Philipp Emanuel},
      title = {Heretic: Fully automatic censorship removal for language models},
      year = {2025},
      publisher = {GitHub},
      journal = {GitHub repository},
      howpublished = {\url{https://github.com/p-e-w/heretic}}
    }

## License

Copyright © 2025-2026 Philipp Emanuel Weidmann ([pew@worldwidemann.com](m...
--
29756:...fero General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

**By contributing to this project, you agree to release your contributions under the same license.**

## About

Fully automatic censorship removal for language models

[heretic-project.org](https://heretic-project.org)

### Topics

[abliteration](/topics/abliteration)[llm](/topics/llm)[transformer](/topics/transformer)

### Resources

Readme

AGPL-3.0 license

[Activity](/p-e-w/heretic/activity)

### Stars...
--
30286:... Watchers

**155** watching

### Forks

[**3.6k** forks](/p-e-w/heretic/forks)

[Report repository](/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fp-e-w%2Fheretic&report=p-e-w+%28user%29)

## Releases

## Used by

## Contributors

## Languages

## Footer

[ ](https://github.com) (C) 2026 GitHub, Inc. 

### Footer navigation

  * [Terms](https://docs.github.com/site-policy/github-terms/github-terms-of-service)
  * [Privacy](https://docs.github.com/site-policy/privacy-policies/github-priva...

# source before running any script: caps BLAS/OpenMP threads (48 default threads on a shared host thrash badly)
export OMP_NUM_THREADS=8 OPENBLAS_NUM_THREADS=8 MKL_NUM_THREADS=8 NUMEXPR_NUM_THREADS=8 TOKENIZERS_PARALLELISM=false

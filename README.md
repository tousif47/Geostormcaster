# Geostormcaster

## Repository structure

`01_data_prep.ipynb` builds the shared hourly foundation: the clean solar
wind series (with physics-derived coupling features) and the 24-hour
window dataset used by Model A, saved as `windows_a.npz`.

`02_model_a_t3h.ipynb` loads those windows and is fully self-contained
from there (baselines, training, threshold sweep, test evaluation).

`03_model_b_t24h.ipynb` builds its own tabular feature table (27-day Kp
lags, F10.7, sunspot number, 24h context) inline at the top of the
notebook — Model B does not use Model A's windows — then trains and
evaluates in the same file.

So: shared window construction lives in 01, Model B's model-specific
features live in 03. Both model notebooks run end-to-end without manual
steps beyond executing cells top to bottom.

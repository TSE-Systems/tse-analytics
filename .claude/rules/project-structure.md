# Project Structure

```
tse_analytics/
├── core/           # data models, messaging, services, workers
├── modules/        # self-contained modules: phenomaster, intellicage, intellimaze
├── toolbox/        # analysis widgets (histogram, ANOVA, PCA, regression, etc.)
├── pipeline/       # node-based visual data processing (NodeGraphQt)
├── views/          # shared UI components and dialogs
├── styles/         # SCSS source → compiled QSS
└── resources/      # app resources (icons, images)
tests/              # pytest suite mirroring source structure
```

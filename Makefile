.PHONY: setup reproduce demo sample clean data

# Setup environment (creates folders & installs deps)
setup:
	pip install -r requirements.txt
	mkdir -p data/raw data/processed data/sample

# Run full reproduction pipeline (expects raw dataset in data/raw/)
reproduce: setup
	python src/preprocessing.py
	python src/analysis.py
	@echo "✅ Analysis complete! Run 'make demo' to launch the dashboard."

# Launch Streamlit dashboard (uses processed data if available; falls back to sample)
demo:
	streamlit run demo/app.py

# Run on bundled sample data (fastest path for reviewers)
sample: setup
	python src/preprocessing.py --sample
	streamlit run demo/app.py

# Clean generated files
clean:
	rm -rf data/processed/*
	rm -rf __pycache__
	rm -rf .ipynb_checkpoints

# Download data instructions (keeps repo lightweight and license-friendly)
data:
	@echo "📥 Download the dataset from:"
	@echo "   UCI Machine Learning Repository: Online Retail II"
	@echo ""
	@echo "   Place the file 'online_retail_II.xlsx' in data/raw/"

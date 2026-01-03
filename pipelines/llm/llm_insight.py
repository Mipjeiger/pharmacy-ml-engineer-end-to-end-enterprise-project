import os
import json
from datetime import datetime

# Setup paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
METRICS_PATH = os.path.join(
    PROJECT_ROOT, "../../notebook/metrics/all_models_metrics.json"
)
OUTPUT_PATH = os.path.join(PROJECT_ROOT, "../../notebook/prompt/insight_prompt.json")


def generate_insights():
    """Generate simple insights from model metrics"""
    print("Generating LLM insights...")

    # Load metrics
    if not os.path.exists(METRICS_PATH):
        print(f"Metrics file not found: {METRICS_PATH}")
        return

    with open(METRICS_PATH, "r") as f:
        metrics = json.load(f)

    # Find best model based on R2 score
    r2_scores = metrics.get("r2_score", {})
    best_model = max(r2_scores, key=r2_scores.get) if r2_scores else "Unknown"
    best_r2 = r2_scores.get(best_model, 0)

    # Generate simple insight
    insight = {
        "timestamp": datetime.now().isoformat(),
        "best_model": best_model,
        "best_r2_score": best_r2,
        "summary": f"Model terbaik: {best_model} dengan R² score {best_r2:.4f}",
        "all_metrics": metrics,
    }

    # Save insight
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(insight, f, indent=2)

    print(f"Insights saved to: {OUTPUT_PATH}")
    print(f"Best Model: {best_model} (R² = {best_r2:.4f})")


if __name__ == "__main__":
    generate_insights()

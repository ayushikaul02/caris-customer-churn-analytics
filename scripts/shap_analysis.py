import sys
import os
sys.path.insert(0, os.getcwd())

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import shap
import warnings
warnings.filterwarnings('ignore')

print("=" * 60)
print("🔬 SHAP Model Explainability Analysis")
print("=" * 60)

# ==================== LOAD DATA ====================
df = pd.read_csv('data/raw/customers_cleaned.csv')
print(f"\n📊 Loaded {len(df)} customers")

# ==================== PREPARE DATA ====================
# Features for churn prediction
feature_cols = ['total_spent', 'monthly_charge', 'age', 'tenure_days']
available_features = [col for col in feature_cols if col in df.columns]

# Create target variable
df['churned'] = (df['status'] == 'churned').astype(int)

# Prepare X and y
X = df[available_features].fillna(0)
y = df['churned']

print(f"\n📈 Features: {list(X.columns)}")
print(f"🎯 Target: Churned (0=No, 1=Yes)")
print(f"📊 Class distribution:\n{y.value_counts().to_dict()}")

# ==================== TRAIN MODEL ====================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, random_state=42, stratify=y
)

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    random_state=42,
    n_jobs=-1
)
model.fit(X_train, y_train)

# Accuracy
accuracy = model.score(X_test, y_test)
print(f"\n✅ Model Accuracy: {accuracy:.2%}")

# ==================== SHAP ANALYSIS ====================
print("\n🔬 Running SHAP analysis...")

# Create SHAP explainer
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X_test)

# Get SHAP values for class 1 (churned)
if isinstance(shap_values, list):
    shap_values_class1 = shap_values[1]
else:
    shap_values_class1 = shap_values

# ==================== PLOT 1: Feature Importance ====================
plt.figure(figsize=(10, 6))
shap.summary_plot(
    shap_values_class1,
    X_test,
    feature_names=available_features,
    show=False,
    plot_size=(10, 6),
    max_display=len(available_features)
)
plt.title('Feature Importance - SHAP Values', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('shap_feature_importance.png', dpi=150, bbox_inches='tight')
print("✅ Saved: shap_feature_importance.png")

# ==================== PLOT 2: Bar Plot ====================
plt.figure(figsize=(10, 6))
shap.summary_plot(
    shap_values_class1,
    X_test,
    feature_names=available_features,
    show=False,
    plot_type="bar",
    plot_size=(10, 6)
)
plt.title('SHAP Feature Importance (Bar)', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('shap_feature_importance_bar.png', dpi=150, bbox_inches='tight')
print("✅ Saved: shap_feature_importance_bar.png")

# ==================== PLOT 3: Waterfall for a Customer ====================
# Pick a high-risk customer
high_risk_customer = X_test.iloc[0]

plt.figure(figsize=(12, 6))
shap.waterfall_plot(
    shap.Explanation(
        values=shap_values_class1[0],
        base_values=explainer.expected_value[1] if isinstance(explainer.expected_value, list) else explainer.expected_value,
        data=high_risk_customer.values,
        feature_names=available_features
    ),
    show=False,
    max_display=len(available_features)
)
plt.title('SHAP Waterfall - Customer Churn Explanation', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('shap_waterfall.png', dpi=150, bbox_inches='tight')
print("✅ Saved: shap_waterfall.png")

# ==================== PLOT 4: Force Plot ====================
plt.figure(figsize=(12, 4))
shap.force_plot(
    explainer.expected_value[1] if isinstance(explainer.expected_value, list) else explainer.expected_value,
    shap_values_class1[0,:],
    X_test.iloc[0,:],
    feature_names=available_features,
    matplotlib=True,
    show=False
)
plt.title('SHAP Force Plot - Individual Prediction', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('shap_force.png', dpi=150, bbox_inches='tight')
print("✅ Saved: shap_force.png")

# ==================== PRINT SUMMARY ====================
print("\n" + "=" * 60)
print("📊 SHAP Analysis Summary")
print("=" * 60)

# Feature importance ranking
feature_importance = pd.DataFrame({
    'Feature': available_features,
    'Importance': model.feature_importances_
}).sort_values('Importance', ascending=False)

print("\n🏆 Feature Importance Ranking:")
for i, row in feature_importance.iterrows():
    print(f"   {row['Feature']}: {row['Importance']:.2%}")

print("\n💡 Key Insights:")
print(f"   • The most important predictor of churn is '{feature_importance.iloc[0]['Feature']}'")
print(f"   • Top 3 features account for {feature_importance.iloc[:3]['Importance'].sum():.1%} of prediction power")

print("\n✅ SHAP analysis complete! Check the generated images.")
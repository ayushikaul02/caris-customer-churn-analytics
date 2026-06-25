# Model Card: Churn Prediction Model

## 📋 Model Overview

| Attribute | Value |
|-----------|-------|
| **Model Name** | Churn Prediction Model v1.0 |
| **Model Type** | Random Forest Classifier |
| **Framework** | Scikit-learn |
| **Task** | Binary Classification (Churn / No Churn) |
| **Training Data** | 1,000 customer records |
| **Test Data** | 300 customer records |

---

## 🎯 Intended Use

- **Primary Use**: Predict which customers are likely to churn
- **Business Impact**: Enable proactive retention strategies
- **Users**: Customer Success Managers, Marketing Teams
- **Decision Support**: Not for automated decision-making

---

## 📊 Performance Metrics

| Metric | Value |
|--------|-------|
| **Accuracy** | 85.0% |
| **Precision** | 82.0% |
| **Recall** | 78.0% |
| **F1-Score** | 80.0% |
| **AUC-ROC** | 0.89 |

---

## 🔍 Feature Importance

| Feature | Importance |
|---------|------------|
| **Total Spent** | 35% |
| **Monthly Charge** | 25% |
| **Tenure Days** | 22% |
| **Age** | 18% |

---

## 📈 SHAP Analysis Insights

### Top 3 Features that Drive Churn:

1. **Total Spent** (+35% impact)
   - Lower spending customers are more likely to churn
   - $500+ increase reduces churn risk by 20%

2. **Monthly Charge** (+25% impact)
   - Customers with high monthly charges are more loyal
   - Each $10 increase reduces churn by 3%

3. **Tenure Days** (+22% impact)
   - Newer customers are at highest risk
   - 90-day mark is critical retention point

---

## ⚠️ Limitations

1. **Data Bias**: Model trained on synthetic data
2. **Generalization**: May not perform well on different customer segments
3. **Temporal**: Does not account for seasonality or external factors
4. **Feature Coverage**: Limited to available features

---

## 🔧 Fairness Considerations

| Group | Performance | Bias Assessment |
|-------|-------------|-----------------|
| Active Customers | F1: 0.82 | No significant bias |
| High-Value Segment | F1: 0.85 | Slightly better performance |
| Low-Value Segment | F1: 0.78 | Monitor for improvement |

---

## 📝 Usage Guidelines

### When to Use:
- ✅ Monthly churn risk assessment
- ✅ Targeted retention campaigns
- ✅ Customer segmentation
- ✅ Business reporting

### When Not to Use:
- ❌ Individual customer decisions
- ❌ Financial credit decisions
- ❌ Automated actions without human review

---

## 🚀 Deployment

| Aspect | Details |
|--------|---------|
| **Environment** | Render Cloud |
| **API Endpoint** | `/api/retention/recommendations` |
| **Authentication** | JWT Required |
| **Response Time** | < 500ms |

---

## 📎 References

- Training Data: `data/raw/customers_cleaned.csv`
- Model Code: `customer_analytics/src/analytics_service.py`
- SHAP Analysis: `scripts/shap_analysis.py`
- Deployment: `app.py`

---

*Last Updated: June 2026*
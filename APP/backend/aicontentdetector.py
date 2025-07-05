import os
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

def detect_ai_content(text):
    """Detect if text is AI-generated using a pre-trained model"""
    try:
        # Get the correct path to the AI content dataset
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(os.path.dirname(current_dir), 'AI CONTENT', 'Training_Essay_Data.csv')
        
        # Fallback to hardcoded path if file doesn't exist
        if not os.path.exists(data_path):
            data_path = r"C:\Users\pushk\OneDrive\Desktop\PLAG AND AI CONTENT DETECTOR PROJECT\APP\AI CONTENT\Training_Essay_Data.csv"
        
        print(f"DEBUG: Using AI content dataset: {data_path}")
        
        # Check if file exists
        if not os.path.exists(data_path):
            return "<div style='background: rgba(220, 53, 69, 0.1); border: 1px solid #DC3545; border-radius: 8px; padding: 20px; margin: 10px 0; text-align: center;'><h3 style='color: #DC3545; margin: 0; font-size: 18px;'>❌ DATASET ERROR</h3><p style='color: #666; margin: 10px 0 0 0;'>AI content dataset not found. Please check the file path.</p></div>"
        
        # Limit text size for processing
        if len(text) > 10000:
            text = text[:10000]
            print("DEBUG: Text truncated to 10K characters for AI detection")
        
        # Load and prepare the dataset
        df = pd.read_csv(data_path).dropna(subset=['text', 'generated'])
        
        # Ensure 'generated' column is numeric
        df['generated'] = pd.to_numeric(df['generated'], errors='coerce').fillna(0).astype(int)
        
        # Train the model
        vectorizer = TfidfVectorizer(max_features=5000)
        X = vectorizer.fit_transform(df['text'])
        y = df['generated']
        
        model = LogisticRegression(max_iter=1000)
        model.fit(X, y)
        
        # Make prediction
        X_input = vectorizer.transform([text])
        prob_ai = model.predict_proba(X_input)[0][1] * 100
        
        # Format result with enhanced styling
        if prob_ai >= 70:
            # High AI probability - red
            color = "#FF4444"
            severity = "HIGH CONFIDENCE"
            icon = "🤖"
            status = "AI-GENERATED"
        elif prob_ai >= 50:
            # Medium AI probability - orange
            color = "#FFA500"
            severity = "MEDIUM CONFIDENCE"
            icon = "⚠️"
            status = "LIKELY AI-GENERATED"
        elif prob_ai >= 30:
            # Low AI probability - yellow
            color = "#FFD700"
            severity = "LOW CONFIDENCE"
            icon = "❓"
            status = "UNCERTAIN"
        else:
            # Human-written - green
            color = "#00FF88"
            severity = "HIGH CONFIDENCE"
            icon = "✅"
            status = "HUMAN-WRITTEN"

        html_output = f"<div style='background: rgba(138, 43, 226, 0.1); border: 1px solid #8A2BE2; border-radius: 8px; padding: 20px; margin: 10px 0;'>"
        html_output += f"<h3 style='color: #8A2BE2; margin: 0 0 15px 0; font-size: 18px;'>{icon} AI CONTENT ANALYSIS</h3>"

        html_output += f"""
        <div style='background: rgba(255, 255, 255, 0.1); border-left: 4px solid {color}; padding: 15px; margin: 10px 0; border-radius: 4px;'>
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                <strong style='color: {color}; font-size: 16px;'>🎯 Detection Result</strong>
                <span style='background: {color}; color: white; padding: 4px 12px; border-radius: 20px; font-weight: bold; font-size: 14px;'>{prob_ai:.1f}% - {severity}</span>
            </div>
            <div style='color: #333; font-size: 14px;'>
                <strong>📊 AI Probability:</strong> {prob_ai:.2f}%<br>
                <strong>🔍 Classification:</strong> {status}<br>
                <strong>💡 Interpretation:</strong> {'This text shows characteristics typical of AI-generated content.' if prob_ai >= 50 else 'This text appears to be written by a human.'}
            </div>
        </div>
        """

        html_output += "</div>"
        return html_output
        
    except Exception as e:
        import traceback
        print(f"ERROR in AI content detection: {str(e)}")
        print(traceback.format_exc())
        return f"<div style='background: rgba(220, 53, 69, 0.1); border: 1px solid #DC3545; border-radius: 8px; padding: 20px; margin: 10px 0; text-align: center;'><h3 style='color: #DC3545; margin: 0; font-size: 18px;'>❌ AI DETECTION ERROR</h3><p style='color: #666; margin: 10px 0 0 0;'>Error in AI content detection: {str(e)}</p></div>"

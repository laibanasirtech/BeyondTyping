#!/usr/bin/env python3
"""
BeyondTyping Intent Classification Model Trainer
===============================================
Trains an ML model to classify voice commands into intents.
Uses TF-IDF vectorization + Logistic Regression for fast, accurate intent detection.
"""

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

def train_intent_model(csv_path="beyond_typing_intents_clean.csv", model_path="intent_model.pkl"):
    """Train intent classification model from CSV dataset"""
    
    print("🚀 Training BeyondTyping Intent Classification Model...")
    print("=" * 60)
    
    # Check if dataset exists
    if not os.path.exists(csv_path):
        print(f"❌ Error: Dataset file '{csv_path}' not found!")
        print("   Please make sure beyond_typing_intents.csv exists in the current directory.")
        return False
    
    try:
        # Load dataset
        print(f"📊 Loading dataset from '{csv_path}'...")
        df = pd.read_csv(csv_path)
        
        if len(df) == 0:
            print("❌ Error: Dataset is empty!")
            return False
        
        print(f"✅ Loaded {len(df)} training examples")
        print(f"📋 Intents found: {df['intent'].nunique()} unique intents")
        
        # Prepare data
        X = df["text"]
        y = df["intent"]
        
        # Split data for evaluation
        # Check if stratification is possible (each class needs at least 2 examples)
        class_counts = y.value_counts()
        min_class_count = class_counts.min()
        
        if min_class_count >= 2:
            # Use stratified split if all classes have at least 2 examples
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
        else:
            # Use regular split if some classes have only 1 example
            print(f"⚠️  Some intents have only 1 example. Using regular split (not stratified).")
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
        
        print(f"\n📚 Training set: {len(X_train)} examples")
        print(f"🧪 Test set: {len(X_test)} examples")
        
        # Train
        print("\n🔧 Training model...")
        print("   - Vectorizing text with TF-IDF...")
        vectorizer = TfidfVectorizer(
            lowercase=True,
            max_features=1000,
            ngram_range=(1, 2),  # Unigrams and bigrams
            min_df=1
        )
        
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)
        
        print("   - Training Logistic Regression classifier...")
        model = LogisticRegression(max_iter=300, random_state=42)
        model.fit(X_train_vec, y_train)
        
        # Evaluate
        print("\n📊 Evaluating model...")
        y_pred = model.predict(X_test_vec)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"✅ Model accuracy: {accuracy:.2%}")
        print("\n📈 Classification Report:")
        print(classification_report(y_test, y_pred))
        
        # Save model
        print(f"\n💾 Saving model to '{model_path}'...")
        with open(model_path, "wb") as f:
            pickle.dump((vectorizer, model), f)
        
        print("✅ Model saved successfully!")
        print(f"\n🎯 Model classes ({len(model.classes_)} intents):")
        for i, intent in enumerate(sorted(model.classes_), 1):
            count = len(df[df['intent'] == intent])
            print(f"   {i:2d}. {intent:25s} ({count} examples)")
        
        print("\n" + "=" * 60)
        print("✅ Training complete! Model ready for use.")
        print(f"   To use in main.py, the model will auto-load from '{model_path}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Install required packages check
    try:
        import pandas as pd
        import sklearn
    except ImportError as e:
        print("❌ Missing required packages!")
        print("   Please install: pip install pandas scikit-learn")
        print(f"   Error: {e}")
        exit(1)
    
    # Train the model
    success = train_intent_model()
    
    if success:
        print("\n🎉 Ready to use ML intent classification!")
        print("   Run: python main.py")
    else:
        print("\n❌ Training failed. Please check the error messages above.")
        exit(1)


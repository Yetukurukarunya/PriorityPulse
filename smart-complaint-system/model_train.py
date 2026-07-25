import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import re
import pickle
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
    
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

# Initialize lemmatizer
lemmatizer = WordNetLemmatizer()

def create_enhanced_dataset():
    """Generate enhanced sample complaint dataset with more features"""
    
    print("Creating enhanced dataset...")
    
    complaints_data = [
        # Emergency complaints (score 9-10)
        ("Medical emergency at city park, person having heart attack", 10, "Emergency", 0),
        ("Fire in residential building downtown, multiple families trapped", 10, "Emergency", 0),
        ("Gas leak reported near school, strong smell of gas", 10, "Emergency", 0),
        ("Building collapse on main street, people trapped under debris", 10, "Emergency", 0),
        ("Active shooter reported in shopping mall", 10, "Emergency", 0),
        ("Child missing from playground, last seen 30 minutes ago", 9, "Emergency", 0),
        ("Severe water contamination, people getting sick", 9, "Emergency", 0),
        ("Major accident on highway with multiple injuries", 9, "Emergency", 0),
        
        # High priority complaints (score 7-8)
        ("Major water pipe burst flooding street", 8, "High Priority", 30),
        ("Road accident with injuries at intersection", 8, "High Priority", 30),
        ("Power outage affecting hospital area", 8, "High Priority", 30),
        ("Sewage overflow on residential street", 7, "High Priority", 60),
        ("Dangerous tree fallen on house", 7, "High Priority", 60),
        ("Electrical short circuit causing sparks", 7, "High Priority", 30),
        ("Blocked emergency exit in building", 7, "High Priority", 60),
        ("Gas smell in residential area", 8, "High Priority", 30),
        
        # Medium priority complaints (score 4-6)
        ("Traffic signal not working at busy intersection", 6, "Medium Priority", 120),
        ("Streetlight not working for 3 days", 5, "Medium Priority", 240),
        ("Pothole causing traffic issues", 5, "Medium Priority", 180),
        ("Garbage not collected for a week", 4, "Medium Priority", 360),
        ("Water leakage from pipeline", 4, "Medium Priority", 240),
        ("Noise complaint from construction site", 4, "Medium Priority", 180),
        ("Parking violations in residential area", 4, "Medium Priority", 300),
        
        # Low priority complaints (score 1-3)
        ("Request for new garbage bin", 2, "Low Priority", 720),
        ("Street name board damaged", 2, "Low Priority", 720),
        ("Public park bench broken", 1, "Low Priority", 1440),
        ("Graffiti on public wall", 1, "Low Priority", 1440),
        ("Street sweeping request", 1, "Low Priority", 720),
        ("Tree trimming request", 2, "Low Priority", 1440),
    ]
    
    # Create variations with additional features
    complaint_texts = []
    severity_scores = []
    categories = []
    expected_resolution_hours = []
    locations = ['Downtown', 'Northside', 'Southside', 'Eastside', 'Westside']
    complaint_types = ['Infrastructure', 'Safety', 'Sanitation', 'Utilities', 'Public Services']
    times_of_day = ['Morning', 'Afternoon', 'Evening', 'Night']
    
    np.random.seed(42)
    
    for text, score, category, resolution_hours in complaints_data:
        # Add multiple variations
        for _ in range(10):  # Generate 10 variations per complaint
            # Add location context
            location = np.random.choice(locations)
            modified_text = f"{text} in {location}"
            complaint_texts.append(modified_text)
            severity_scores.append(score + np.random.uniform(-0.3, 0.3))
            categories.append(category)
            expected_resolution_hours.append(resolution_hours)
            
            # Add with urgency prefix for high severity
            if score >= 8:
                urgent_text = f"URGENT: {text} in {location}"
                complaint_texts.append(urgent_text)
                severity_scores.append(score + np.random.uniform(-0.2, 0.2))
                categories.append(category)
                expected_resolution_hours.append(resolution_hours * 0.5)  # Faster response for urgent
            
            # Add with complaint type
            complaint_type = np.random.choice(complaint_types)
            type_text = f"{complaint_type} issue: {text}"
            complaint_texts.append(type_text)
            severity_scores.append(score + np.random.uniform(-0.2, 0.2))
            categories.append(category)
            expected_resolution_hours.append(resolution_hours)
    
    # Create DataFrame with additional features
    df = pd.DataFrame({
        'complaint_text': complaint_texts,
        'severity_score': np.clip(severity_scores, 1, 10).round(1),
        'category': categories,
        'expected_resolution_hours': expected_resolution_hours,
        'location': np.random.choice(locations, len(complaint_texts)),
        'complaint_type': np.random.choice(complaint_types, len(complaint_texts)),
        'time_of_day': np.random.choice(times_of_day, len(complaint_texts)),
        'latitude': np.random.uniform(40.7128, 40.7589, len(complaint_texts)),
        'longitude': np.random.uniform(-74.0060, -73.9352, len(complaint_texts)),
        'date': [datetime(2024, 1, 1) + timedelta(hours=i) for i in range(len(complaint_texts))]
    })
    
    # Add derived features
    df['text_length'] = df['complaint_text'].str.len()
    df['word_count'] = df['complaint_text'].str.split().str.len()
    df['has_urgent'] = df['complaint_text'].str.contains('urgent|emergency|immediate', case=False).astype(int)
    df['has_location'] = df['complaint_text'].str.contains('|'.join(locations), case=False).astype(int)
    
    print(f"✓ Created enhanced dataset with {len(df)} samples")
    print(f"✓ Features: {', '.join(df.columns)}")
    
    return df

def advanced_preprocess_text(text):
    """Advanced text preprocessing with lemmatization"""
    # Convert to lowercase
    text = str(text).lower()
    
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Remove stopwords and lemmatize
    stop_words = set(stopwords.words('english'))
    words = text.split()
    words = [lemmatizer.lemmatize(w) for w in words if w not in stop_words and len(w) > 2]
    
    return ' '.join(words)

def train_enhanced_model():
    """Train enhanced complaint severity prediction model"""
    
    print("=" * 60)
    print("SMART COMPLAINT PRIORITIZATION SYSTEM - ENHANCED MODEL")
    print("=" * 60)
    
    # Create directories
    os.makedirs('data', exist_ok=True)
    os.makedirs('models', exist_ok=True)
    
    # Create or load dataset
    csv_path = 'data/complaints_enhanced.csv'
    
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print(f"✓ Loaded existing dataset: {len(df)} samples")
    else:
        df = create_enhanced_dataset()
        df.to_csv(csv_path, index=False)
        print(f"✓ Created new dataset: {len(df)} samples")
    
    print(f"\nDataset Overview:")
    print(f"  Total samples: {len(df)}")
    print(f"  Features: {len(df.columns)}")
    print(f"\nSeverity Score Distribution:")
    print(df['severity_score'].describe())
    print(f"\nCategory Distribution:")
    print(df['category'].value_counts())
    
    # Preprocess text
    print("\nPreprocessing text with advanced NLP...")
    df['processed_text'] = df['complaint_text'].apply(advanced_preprocess_text)
    
    # Prepare features
    X_text = df['processed_text']
    X_categorical = df[['complaint_type', 'time_of_day']]
    X_numerical = df[['text_length', 'word_count', 'has_urgent', 'has_location']]
    y = df['severity_score']
    
    # Encode categorical features
    le_complaint = LabelEncoder()
    le_time = LabelEncoder()
    
    X_categorical_encoded = pd.DataFrame({
        'complaint_type': le_complaint.fit_transform(X_categorical['complaint_type']),
        'time_of_day': le_time.fit_transform(X_categorical['time_of_day'])
    })
    
    # Combine features
    X_combined = pd.concat([X_numerical, X_categorical_encoded], axis=1)
    
    # Split data
    X_train_text, X_test_text, X_train_combined, X_test_combined, y_train, y_test = train_test_split(
        X_text, X_combined, y, test_size=0.2, random_state=42
    )
    
    # Vectorize text
    print("\nVectorizing text with TF-IDF...")
    vectorizer = TfidfVectorizer(
        max_features=1500,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.85
    )
    X_train_text_vectorized = vectorizer.fit_transform(X_train_text)
    X_test_text_vectorized = vectorizer.transform(X_test_text)
    
    # Combine text and numerical features
    from scipy.sparse import hstack
    X_train_final = hstack([X_train_text_vectorized, X_train_combined.values])
    X_test_final = hstack([X_test_text_vectorized, X_test_combined.values])
    
    # Train enhanced model with hyperparameter tuning
    print("\nTraining Gradient Boosting model with hyperparameter tuning...")
    
    # Use Gradient Boosting for better accuracy
    model = GradientBoostingRegressor(
        n_estimators=150,
        learning_rate=0.1,
        max_depth=5,
        min_samples_split=4,
        min_samples_leaf=2,
        random_state=42,
        subsample=0.8
    )
    
    model.fit(X_train_final, y_train)
    
    # Evaluate
    print("\nEvaluating model...")
    y_pred = model.predict(X_test_final)
    
    # Calculate metrics
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    accuracy_within_1 = np.mean(np.abs(y_test - y_pred) <= 1) * 100
    
    print(f"\n✓ Model Performance Metrics:")
    print(f"  Mean Absolute Error (MAE): {mae:.3f}")
    print(f"  Root Mean Squared Error (RMSE): {rmse:.3f}")
    print(f"  R² Score: {r2:.3f}")
    print(f"  Accuracy (within ±1 point): {accuracy_within_1:.1f}%")
    
    # Cross-validation
    print("\nPerforming cross-validation...")
    cv_scores = cross_val_score(model, X_train_final, y_train, cv=5, scoring='r2')
    print(f"  Cross-validation R² scores: {cv_scores}")
    print(f"  Average CV R²: {cv_scores.mean():.3f} (+/- {cv_scores.std() * 2:.3f})")
    
    # Save model artifacts
    print("\nSaving model artifacts...")
    with open('models/complaint_model_enhanced.pkl', 'wb') as f:
        pickle.dump(model, f)
    
    with open('models/vectorizer_enhanced.pkl', 'wb') as f:
        pickle.dump(vectorizer, f)
    
    with open('models/label_encoders.pkl', 'wb') as f:
        pickle.dump({'complaint_type': le_complaint, 'time_of_day': le_time}, f)
    
    print("✓ Model saved to: models/complaint_model_enhanced.pkl")
    print("✓ Vectorizer saved to: models/vectorizer_enhanced.pkl")
    print("✓ Label encoders saved to: models/label_encoders.pkl")
    
    # Feature importance analysis
    print("\nFeature Importance Analysis:")
    feature_names = list(vectorizer.get_feature_names_out()) + \
                    ['text_length', 'word_count', 'has_urgent', 'has_location', 
                     'complaint_type_encoded', 'time_of_day_encoded']
    
    importance = model.feature_importances_
    top_indices = np.argsort(importance)[-15:][::-1]
    
    print("Top 15 Most Important Features:")
    for idx in top_indices[:15]:
        if idx < len(feature_names):
            print(f"  {feature_names[idx]}: {importance[idx]:.4f}")
    
    # Test predictions with sample complaints
    print("\n" + "=" * 60)
    print("TESTING MODEL WITH SAMPLE COMPLAINTS")
    print("=" * 60)
    
    test_complaints = [
        "Emergency! Fire in the building downtown with people trapped",
        "Water pipe burst on main street flooding the area",
        "Streetlight not working for a week on Oak Street",
        "Request for new garbage bin in my neighborhood",
        "Medical emergency at city park, person having heart attack",
        "Pothole on the road causing accidents near school",
        "Gas leak smell near residential area, immediate attention needed"
    ]
    
    for complaint in test_complaints:
        try:
            processed = advanced_preprocess_text(complaint)
            text_vectorized = vectorizer.transform([processed])
            
            # Extract features for the complaint
            text_len = len(complaint)
            word_count = len(complaint.split())
            has_urgent = 1 if any(word in complaint.lower() for word in ['urgent', 'emergency', 'immediate']) else 0
            has_location = 1 if any(loc in complaint.lower() for loc in locations) else 0
            
            # Create feature array
            combined_features = np.array([[text_len, word_count, has_urgent, has_location, 0, 0]])
            X_test = hstack([text_vectorized, combined_features])
            
            severity = model.predict(X_test)[0]
            
            # Determine priority
            if severity >= 8:
                priority = "EMERGENCY"
                response_time = "Immediate (0-1 hour)"
                color = "danger"
            elif severity >= 5:
                priority = "HIGH PRIORITY"
                response_time = "Urgent (1-4 hours)"
                color = "warning"
            elif severity >= 3:
                priority = "MEDIUM PRIORITY"
                response_time = "Normal (4-24 hours)"
                color = "info"
            else:
                priority = "LOW PRIORITY"
                response_time = "Scheduled (24-72 hours)"
                color = "success"
            
            print(f"\n  Complaint: '{complaint[:60]}...'")
            print(f"  Severity Score: {severity:.1f}/10")
            print(f"  Priority: {priority}")
            print(f"  Response Time: {response_time}")
            print(f"  Color Code: {color}")
            
        except Exception as e:
            print(f"\n  Error predicting: {e}")
    
    print("\n" + "=" * 60)
    print("✓ Enhanced model training completed successfully!")
    print("=" * 60)
    
    return model, vectorizer

if __name__ == "__main__":
    train_enhanced_model()
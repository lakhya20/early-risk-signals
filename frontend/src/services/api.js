const API_BASE = "http://127.0.0.1:8000";

export const api = {
  score: API_BASE + "/score/predict",
  train: API_BASE + "/train/",
  history: API_BASE + "/train/history",
  versions: API_BASE + "/train/versions",
  rollback: (version) => API_BASE + `/train/rollback/${version}`,
  customer: (id) => API_BASE + `/customer/${id}`,
  alerts: (id) => API_BASE + `/alerts/${id}`,
};

// Helper function for API calls
export const apiCall = async (url, options = {}) => {
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(error || 'API request failed');
    }

    return await response.json();
  } catch (error) {
    console.error('API Error:', error);
    throw error;
  }
};

// Score prediction
export const scoreCustomer = async (data) => {
  return apiCall(api.score, {
    method: 'POST',
    body: JSON.stringify(data),
  });
};

// Train model
export const trainModel = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(api.train, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(error || 'Training failed');
  }

  return await response.json();
};

// Get training history
export const getTrainingHistory = async () => {
  return apiCall(api.history);
};

// Get model versions
export const getModelVersions = async () => {
  return apiCall(api.versions);
};

// Rollback model
export const rollbackModel = async (version) => {
  return apiCall(api.rollback(version), {
    method: 'POST',
  });
};

// Get customer
export const getCustomer = async (id) => {
  return apiCall(api.customer(id));
};

// Get alerts
export const getAlerts = async (id) => {
  return apiCall(api.alerts(id));
};

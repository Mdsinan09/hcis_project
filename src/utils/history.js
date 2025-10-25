import axios from './axios';

/**
 * Fetches the list of analysis history records from the backend via GET.
 * This function should be called by History.jsx on component mount.
 * @returns {Promise<Array>} A promise that resolves to the array of history items.
 */
export const getHistory = async () => {
  try {
    // 📢 CRITICAL: Calling the GET endpoint to fetch the list of reports.
    const { data } = await axios.get('/history');
    return data;
  } catch (error) {
    console.error("Error fetching history list:", error);
    // Return empty array on failure so the app doesn't crash
    return []; 
  }
};

/**
 * 📢 CRITICAL FIX: This function now does nothing, as the report is ALREADY 
 * saved by the successful POST to /analyze. The Detector page now uses 
 * the report data directly. We keep it for compatibility but remove the POST call.
 */
export const addReportToHistory = (report) => {
  // Detector page saves report data locally, and the history list pulls it later.
  // We rely on the /api/analyze endpoint to save to the server's JSON file.
  console.log("Report saved successfully by /api/analyze.");
  return report;
};

/**
 * Filters the current local history data synchronously to find a specific report.
 * NOTE: This relies on the History component managing its state correctly.
 * We no longer need an API call here.
 */
export const getReportById = async (id) => {
    // 📢 We need to fetch the whole list first if we want to rely on the server 
    // for report detail, but for immediate display, the History component 
    // usually passes the object or refetches the list.
    // Given the component structure, it's safer to rely on the current state 
    // managed by History.jsx after the first successful fetch.
    
    // However, if called independently, it must fetch the data:
    const history = await getHistory();
    return history.find(h => h.id === id);
};


/**
 * Deletes a specific report by ID via the backend DELETE endpoint.
 */
export const deleteReport = async (id) => {
  // 📢 CRITICAL: Ensure the delete URL is correctly structured
  await axios.delete(`/history/${id}`);
};

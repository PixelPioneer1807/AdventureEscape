import axios from "axios";

export const logEvent = async ({ storyId, eventType, payload }) => {
  try {
    await axios.post("/api/analytics/event", {
      story_id: storyId,
      event_type: eventType,
      payload
    });
  } catch (err) {
    console.error("Analytics log failed:", err);
  }
};

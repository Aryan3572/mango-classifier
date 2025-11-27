// src/utils/auth.js

export const saveToken = (token) => {
  localStorage.setItem("mango_token", token);
};

export const getToken = () => {
  return localStorage.getItem("mango_token");
};

export const removeToken = () => {
  localStorage.removeItem("mango_token");
};

export const authHeader = () => {
  const t = getToken();
  return t
    ? { Authorization: `Bearer ${t}`, "Content-Type": "application/json" }
    : { "Content-Type": "application/json" };
};

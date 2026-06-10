import api from './request';

export const authApi = {
  getFeishuLoginUrl: () => api.get('/auth/feishu/login'),
  feishuCallback: (code: string) => api.get(`/auth/feishu/callback?code=${code}`),
  devLogin: (data: { username: string; is_admin?: boolean }) => api.post('/auth/dev-login', data),
  getMe: () => api.get('/auth/me'),
  logout: () => api.post('/auth/logout'),
};

export const skillApi = {
  getList: (params: { page: number; page_size: number; keyword?: string }) =>
    api.get('/skills', { params }),
  getDetail: (id: number) => api.get(`/skills/${id}`),
  getTools: (id: number) => api.get(`/skills/${id}/tools`),
};

export const toolApi = {
  getList: (params: { page: number; page_size: number; keyword?: string; skill_id?: number }) =>
    api.get('/tools', { params }),
  getDetail: (id: number) => api.get(`/tools/${id}`),
};

export const permissionApi = {
  createRequest: (data: { type: string; target_id: number; reason?: string }) =>
    api.post('/permission-requests', data),
  getMyRequests: (params: { page: number; page_size: number }) =>
    api.get('/permission-requests', { params }),
  cancelRequest: (id: number) => api.delete(`/permission-requests/${id}`),
};

export const userApi = {
  getPermissions: () => api.get('/users/me/permissions'),
  getRoles: () => api.get('/users/me/roles'),
};

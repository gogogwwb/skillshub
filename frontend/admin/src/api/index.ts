import api from './request';

export const authApi = {
  getFeishuLoginUrl: () => api.get('/auth/feishu/login'),
  feishuCallback: (code: string) => api.get(`/auth/feishu/callback?code=${code}`),
  devLogin: (data: { username: string; is_admin?: boolean }) => api.post('/auth/dev-login', data),
  getMe: () => api.get('/auth/me'),
  logout: () => api.post('/auth/logout'),
};

export const userApi = {
  getList: (params: { page: number; page_size: number; keyword?: string }) =>
    api.get('/admin/users', { params }),
  getDetail: (id: number) => api.get(`/admin/users/${id}`),
  updateRoles: (id: number, role_ids: number[]) => api.put(`/admin/users/${id}/roles`, { role_ids }),
  updateStatus: (id: number, status: string) => api.put(`/admin/users/${id}/status`, { status }),
};

export const roleApi = {
  getList: () => api.get('/admin/roles'),
  create: (data: { name: string; description?: string }) => api.post('/admin/roles', data),
  update: (id: number, data: { name?: string; description?: string }) => api.put(`/admin/roles/${id}`, data),
  delete: (id: number) => api.delete(`/admin/roles/${id}`),
  assignSkills: (id: number, skill_ids: number[]) => api.put(`/admin/roles/${id}/skills`, { skill_ids }),
  assignTools: (id: number, tool_ids: number[]) => api.put(`/admin/roles/${id}/tools`, { tool_ids }),
};

export const skillApi = {
  getList: (params: { page: number; page_size: number; keyword?: string; status?: string }) =>
    api.get('/admin/skills', { params }),
  create: (data: { name: string; description?: string; config?: any }) => api.post('/admin/skills', data),
  update: (id: number, data: any) => api.put(`/admin/skills/${id}`, data),
  delete: (id: number) => api.delete(`/admin/skills/${id}`),
};

export const toolApi = {
  getList: (params: { page: number; page_size: number; keyword?: string; skill_id?: number; status?: string }) =>
    api.get('/admin/tools', { params }),
  create: (data: any) => api.post('/admin/tools', data),
  update: (id: number, data: any) => api.put(`/admin/tools/${id}`, data),
  delete: (id: number) => api.delete(`/admin/tools/${id}`),
};

export const approvalApi = {
  getList: (params: { page: number; page_size: number; status?: string }) =>
    api.get('/admin/approvals', { params }),
  approve: (id: number, comment?: string) => api.put(`/admin/approvals/${id}/approve`, { comment }),
  reject: (id: number, comment?: string) => api.put(`/admin/approvals/${id}/reject`, { comment }),
};

export const departmentApi = {
  getTree: () => api.get('/admin/departments'),
  sync: () => api.post('/admin/departments/sync'),
};

export const auditApi = {
  getList: (params: { page: number; page_size: number; action?: string; target_type?: string }) =>
    api.get('/admin/audit-logs', { params }),
};

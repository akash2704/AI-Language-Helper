export interface ApiError {
  response?: {
    data?: {
      message?: string;
      [key: string]: any;
    };
  };
  message?: string;
  [key: string]: any;
}

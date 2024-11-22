import 'datatables.net';

declare module 'datatables.net' {
  interface Config {
    fixedColumns?: any;
  }
}

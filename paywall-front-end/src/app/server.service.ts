import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpHeaders } from '@angular/common/http';
import { throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class ServerService {
  public serverUrl: string = "http://127.0.0.1:8000/";

  constructor(private http: HttpClient) { }

  fetchData(_paymentId: string) {
    const body = {
      id: _paymentId,
    };
    const headers = new HttpHeaders().set('Content-Type', 'application/json');

    return this.http.post(this.serverUrl + "get_payment_request_by_id_public/", body, { headers: headers })
      .pipe(
        catchError(error => {
          console.error('Error fetching data:', error);
          return throwError(error);
        })
      );
  }



  fetchBtcPrice() {
    const headers = new HttpHeaders().set('Content-Type', 'application/json');

    return this.http.get(this.serverUrl + "get_coins_rate/", { headers: headers })
      .pipe(
        catchError(error => {
          console.error('Error fetching BTC price:', error);
          return throwError(error);
        })
      );
  }
}

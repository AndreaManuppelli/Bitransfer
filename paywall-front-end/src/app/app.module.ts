// PrimeNg imports
import { ProgressSpinnerModule } from 'primeng/progressspinner';
import { ButtonModule } from 'primeng/button';

// QR Code
import { NgxQrcodeStylingModule } from 'ngx-qrcode-styling';

// Particles
import { NgParticlesModule } from 'ng-particles';

// Genaral imports
import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { PaymentComponent } from './payment/payment.component';

@NgModule({
  declarations: [
    AppComponent,
    PaymentComponent
  ],
  imports: [
    // PrimeNg
    ProgressSpinnerModule,
    ButtonModule,
    // QR Code
    NgxQrcodeStylingModule,
    // Particles
    NgParticlesModule,

    BrowserModule,
    AppRoutingModule,
    HttpClientModule,
    BrowserAnimationsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }

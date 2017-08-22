// Fitting tools: Sub-rootins

#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>

#define  DIM   5

// Solving Linear Equation (Lapack)
int dgesv_(long *, long *, double *, long * , long *, double *, long *, long *);


// Initialize parameters:
//    f(x)= ( par[0]+ par[1]* sin( pi*(x+par[2])/12 ) )* pow(x, par[3])* exp(- x/par[4])
void  init_par( int num, const double y[], double par[] )
{
  int   i;     double   max= 0, t_p= 0.5;

  for (i=0; i<num; i++)
    {
      if ( y[i]> max )     {   max= y[i];     t_p= i+0.5;   }
    }

  par[2]= 1.0;     par[3]= 2.0;      // Set phi_0 and k
  // par[2]= 1.0;     par[3]= 0.1;      // Set phi_0 and k

  // Set tau from the peak position.
  par[4]= t_p/par[3];
  // Set a and b from the peak value.
  par[0]= max/ pow( t_p, par[3])* exp( t_p/par[4] );     par[1]= 0.2* par[0];
}


// Gradient and Hessian of the Function:
//    f(x)= ( par[0]+ par[1]* sin( pi*(x+par[2])/12 ) )* pow(x, par[3])* exp(- x/par[4])
double calc_FH( int num, const double x[], const double y[], const double par[], double grad[], double H[])
{
  int     i= 1, j, k, n= DIM;
  // Initialize: grad, H
  for (i=0; i<n;   i++)  grad[i]= 0;
  for (i=0; i<n*n; i++)  H[i]= 0;

  // Calc. Gradient: F_x, Hessian: J_x.
  double  err, f_x, f_sin, f_cos, f_dg, w[DIM], sum= 0;
  for (i=0; i<num; i++)
    {
      f_dg=   pow( x[i], par[3] )* exp( (-1)* x[i]/par[4] );
      f_sin=  sin( M_PI* (x[i]+ par[2])/ 12.0 );
      f_cos=  cos( M_PI* (x[i]+ par[2])/ 12.0 );

      f_x=  ( par[0]+ par[1]* f_sin )* f_dg;     err= y[i]- f_x;

      // Set w[*]: Derivative of Fitting Fun.
      w[0]= f_dg;     w[1]= f_sin* f_dg;     w[2]= M_PI/12.0* par[1]* f_cos* f_dg;
      w[3]= f_x* log( x[i]);                 w[4]= f_x* x[i]/ par[4]/ par[4];

      // grad_j = ¥sum err* df/d¥theta_k
      for (j=0; j<n;j++)          {  grad[j] += err* w[j];   }
      // H_{jk} = df/d¥theta_j * df/d¥theta_k
      for (j=0; j<n; j++)
	{
	  for (k=0; k<= j; k++)   {  H[j+k*n] += w[j]* w[k];   }
	}

      sum += err*err;        // sum: Error (Proposed model)
    }

  return   sum/num;
}


// Fitting via Levenberg-Marquardt method: Derivative of Gamma function
double  solv_LM( int num, const double x[], const double y[], double *c_LM, double par[])
{
  int     i, j;      long    n= DIM, inc=1, info=1;
  long    piv[n];    double  F_x[n], J_x[n*n], err_o;

  err_o= calc_FH( num, x, y, par, F_x, J_x);

  for (i= 0; i<n; i++)  //  Modify Hessian: LM-method
    {
      J_x[ (n+1)*i ]= (1+ (*c_LM) )* J_x[ (n+1)*i ];
      for (j= i+1; j<n; j++)     J_x[ i+n*j ]= J_x[ j+n*i ];  // Non-Diag
    }

  // Solv. Eqs.
  dgesv_( &n, &inc, J_x, &n, piv, F_x, &n, &info);

  double  p_o[n], err_n= 0, eps= 1;
  if ( info==0 )  // Evaluate Errors:
    {
      for(i=0; i<n; i++)
	{  p_o[i]= par[i];   par[i]+= F_x[i];  }

      // 0< t_0 < 24, 0< k, 5< tau
      if ( par[0]< pow( 0.1, 7) )       par[0]= pow( 0.1, 7);
      if ( par[1]< pow( 0.1, 7) )       par[1]= pow( 0.1, 7);
      if ( par[2]< 0  || par[2]> 24 )   par[2]= 0;
      if ( par[3]< 0  )   par[3]= 0;
      if ( par[4]< 5  )   par[4]= 5;

      // Evaluate Error for the new parameters:
      err_n= calc_FH( num, x, y, par, F_x, J_x);
      eps= fabs( err_o- err_n);

      if ( err_n > err_o )   // No improvement:
	{
	  *c_LM= 10* (*c_LM);   eps= 1;
	  for (i=0; i<n; i++)  {  par[i]= p_o[i];  }
	}
      else   {  *c_LM= (*c_LM)/10;    }
    }
  else
    {  *c_LM= 10* (*c_LM);   eps= 1;   }

  // Check for the exact singularity.
  if( info > 0 ) {   eps= 100;  }

  return eps;
}

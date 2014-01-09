/*=========================================================================

  Program:   Insight Segmentation & Registration Toolkit
  Module:    $RCSfile: itkAffineTransform.h,v $
  Language:  C++
  Date:      $Date: 2007-01-25 23:18:04 $
  Version:   $Revision: 1.68 $

  Copyright (c) Insight Software Consortium. All rights reserved.
  See ITKCopyright.txt or http://www.itk.org/HTML/Copyright.htm for details.

     This software is distributed WITHOUT ANY WARRANTY; without even 
     the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR 
     PURPOSE.  See the above copyright notices for more information.

=========================================================================*/

#ifndef __itkAffineTransform_h
#define __itkAffineTransform_h

#include <iostream>

#include "itkMatrix.h"
#include "itkMatrixOffsetTransformBase.h"
#include "itkExceptionObject.h"
#include "itkMacro.h"

namespace itk
{


/**
 * Affine transformation of a vector space (e.g. space coordinates)
 *
 * This class allows the definition and manipulation of affine
 * transformations of an n-dimensional affine space (and its
 * associated vector space) onto itself.  One common use is to define
 * and manipulate Euclidean coordinate transformations in two and
 * three dimensions, but other uses are possible as well.
 *
 * An affine transformation is defined mathematically as a linear
 * transformation plus a constant offset.  If A is a constant n x n
 * matrix and b is a constant n-vector, then y = Ax+b defines an
 * affine transformation from the n-vector x to the n-vector y.
 *
 * The difference between two points is a vector and transforms
 * linearly, using the matrix only.  That is, (y1-y2) = A*(x1-x2).
 *
 * The AffineTransform class determines whether to transform an object
 * as a point or a vector by examining its type.  An object of type
 * Point transforms as a point; an object of type Vector transforms as
 * a vector.
 *
 * One common use of affine transformations is to define coordinate
 * conversions in two- and three-dimensional space.  In this
 * application, x is a two- or three-dimensional vector containing the
 * "source" coordinates of a point, y is a vector containing the
 * "target" coordinates, the matrix A defines the scaling and rotation
 * of the coordinate systems from the source to the target, and b
 * defines the translation of the origin from the source to the
 * target.  More generally, A can also define anisotropic scaling and
 * shearing transformations.  Any good textbook on computer graphics
 * will discuss coordinate transformations in more detail.  Several of
 * the methods in this class are designed for this purpose and use the
 * language appropriate to coordinate conversions.
 *
 * Any two affine transformations may be composed and the result is
 * another affine transformation.  However, the order is important.
 * Given two affine transformations T1 and T2, we will say that
 * "precomposing T1 with T2" yields the transformation which applies
 * T1 to the source, and then applies T2 to that result to obtain the
 * target.  Conversely, we will say that "postcomposing T1 with T2"
 * yields the transformation which applies T2 to the source, and then
 * applies T1 to that result to obtain the target.  (Whether T1 or T2
 * comes first lexicographically depends on whether you choose to
 * write mappings from right-to-left or vice versa; we avoid the whole
 * problem by referring to the order of application rather than the
 * textual order.)
 *
 * There are two template parameters for this class:
 *
 * ScalarT       The type to be used for scalar numeric values.  Either
 *               float or double.
 *
 * NDimensions   The number of dimensions of the vector space.
 *
 * This class provides several methods for setting the matrix and vector
 * defining the transform. To support the registration framework, the 
 * transform parameters can also be set as an Array<double> of size
 * (NDimension + 1) * NDimension using method SetParameters(). 
 * The first (NDimension x NDimension) parameters defines the matrix in 
 * column-major order (where the column index) varies the fastest). 
 * The last NDimension parameters defines the translation 
 * in each dimensions.
 *
 * This class also supports the specification of a center of rotation (center)
 * and a translation that is applied with respect to that centered rotation.
 * By default the center of rotation is set to the origin.
 *
 * \ingroup Transforms
 *
 **/

template <
 class TScalarType=double,         // Data type for scalars 
                                   //    (e.g. float or double)
 unsigned int NDimensions=3>       // Number of dimensions in the input space
class AffineTransform 
: public MatrixOffsetTransformBase< TScalarType, NDimensions, NDimensions >
{
public:
  /** Standard typedefs   */
  typedef AffineTransform                           Self;
  typedef MatrixOffsetTransformBase< TScalarType,
                                     NDimensions,
                                     NDimensions >  Superclass;
  typedef SmartPointer<Self>                        Pointer;
  typedef SmartPointer<const Self>                  ConstPointer;
  
  /** Run-time type information (and related methods).   */
  itkTypeMacro( AffineTransform, MatrixOffsetTransformBase );

  /** New macro for creation of through a Smart Pointer   */
  itkNewMacro( Self );

  /** Dimension of the domain space. */
  itkStaticConstMacro(InputSpaceDimension, unsigned int, NDimensions);
  itkStaticConstMacro(OutputSpaceDimension, unsigned int, NDimensions);
  itkStaticConstMacro(SpaceDimension, unsigned int, NDimensions);
  itkStaticConstMacro(ParametersDimension, unsigned int,
                                           NDimensions*(NDimensions+1));

  
  /** Parameters Type   */
  typedef typename Superclass::ParametersType         ParametersType;
  typedef typename Superclass::JacobianType           JacobianType;
  typedef typename Superclass::ScalarType             ScalarType;
  typedef typename Superclass::InputPointType         InputPointType;
  typedef typename Superclass::OutputPointType        OutputPointType;
  typedef typename Superclass::InputVectorType        InputVectorType;
  typedef typename Superclass::OutputVectorType       OutputVectorType;
  typedef typename Superclass::InputVnlVectorType     InputVnlVectorType;
  typedef typename Superclass::OutputVnlVectorType    OutputVnlVectorType;
  typedef typename Superclass::InputCovariantVectorType 
                                                      InputCovariantVectorType;
  typedef typename Superclass::OutputCovariantVectorType
                                                      OutputCovariantVectorType;
  typedef typename Superclass::MatrixType             MatrixType;
  typedef typename Superclass::InverseMatrixType      InverseMatrixType;
  typedef typename Superclass::CenterType             CenterType;
  typedef typename Superclass::OffsetType             OffsetType;
  typedef typename Superclass::TranslationType        TranslationType;

  /** Compose affine transformation with a translation
   *
   * This method modifies self to include a translation of the
   * origin.  The translation is precomposed with self if pre is
   * true, and postcomposed otherwise. 
   * This updates Translation based on current center. */
  void Translate(const OutputVectorType &offset, bool pre=0);

  /** Compose affine transformation with a scaling
   *
   * This method modifies self to magnify the source by a given
   * factor along each axis.  If all factors are the same, or only a
   * single factor is given, then the scaling is isotropic;
   * otherwise it is anisotropic.  If an odd number of factors are
   * negative, then the parity of the image changes.  If any of the
   * factors is zero, then the transformation becomes a projection
   * and is not invertible.  The scaling is precomposed with self if
   * pre is true, and postcomposed otherwise. 
   * Note that the scaling is applied centered at the origin. */
  void Scale(const OutputVectorType &factor, bool pre=0);
  void Scale(const TScalarType &factor, bool pre=0);

  /** Compose affine transformation with an elementary rotation
   *
   * This method composes self with a rotation that affects two
   * specified axes, replacing the current value of self.  The
   * rotation angle is in radians.  The axis of rotation goes
   * through the origin.  The transformation is given by
   *
   * y[axis1] =  vcl_cos(angle)*x[axis1] + vcl_sin(angle)*x[axis2]
   * y[axis2] = -sin(angle)*x[axis1] + vcl_cos(angle)*x[axis2].
   *
   * All coordinates other than axis1 and axis2 are unchanged;
   * a rotation of pi/2 radians will carry +axis1 into +axis2.
   * The rotation is precomposed with self if pre is true, and
   * postcomposed otherwise. 
   * Note that the rotation is applied centered at the origin. */
  void Rotate(int axis1, int axis2, TScalarType angle, bool pre=0);

  /** Compose 2D affine transformation with a rotation
   *
   * This method composes self, which must be a 2D affine
   * transformation, with a clockwise rotation through a given angle
   * in radians.  The center of rotation is the origin.  The
   * rotation is precomposed with self if pre is true, and
   * postcomposed otherwise.
   * Note that the rotation is applied centered at the origin.
   *
   * \warning Only to be use in two dimensions
   *
   * \todo Find a way to generate a compile-time error
   *       is this is used with NDimensions != 2. */
  void Rotate2D(TScalarType angle, bool pre=0);

  /** Compose 3D affine transformation with a rotation
   *
   * This method composes self, which must be a 3D affine
   * transformation, with a clockwise rotation around a specified
   * axis.  The rotation angle is in radians; the axis of rotation
   * goes through the origin.  The rotation is precomposed with self
   * if pre is true, and postcomposed otherwise.
   * Note that the rotation is applied centered at the origin.
   *
   * \warning Only to be used in dimension 3
   *
   * \todo Find a way to generate a compile-time error
   * is this is used with NDimensions != 3. */
  void Rotate3D(const OutputVectorType &axis, TScalarType angle, bool pre=0);

  /** Compose affine transformation with a shear
   *
   * This method composes self with a shear transformation,
   * replacing the original contents of self.  The shear is
   * precomposed with self if pre is true, and postcomposed
   * otherwise.  The transformation is given by
   *
   * y[axis1] = x[axis1] + coef*x[axis2]
   * y[axis2] =                 x[axis2]. 
   *
   * Note that the shear is applied centered at the origin. */
  void Shear(int axis1, int axis2, TScalarType coef, bool pre=0);

  /** Back transform by an affine transformation
   *
   * This method finds the point or vector that maps to a given
   * point or vector under the affine transformation defined by
   * self.  If no such point exists, an exception is thrown.   
   *
   * \deprecated Please use GetInverseTransform and then call the
   *   forward transform function **/
  inline InputPointType   BackTransform(const OutputPointType  &point ) const;
  inline InputVectorType  BackTransform(const OutputVectorType &vector) const;
  inline InputVnlVectorType BackTransform(
                                     const OutputVnlVectorType &vector) const;
  inline InputCovariantVectorType BackTransform(
                              const OutputCovariantVectorType &vector) const;

  /** Back transform a point by an affine transform
   *
   * This method finds the point that maps to a given point under
   * the affine transformation defined by self.  If no such point
   * exists, an exception is thrown.  The returned value is (a
   * pointer to) a brand new point created with new. 
   *
   * \deprecated Please use GetInverseTransform and then call the
   *   forward transform function **/
  inline InputPointType BackTransformPoint(const OutputPointType  &point) const;

  /** Compute distance between two affine transformations
   *
   * This method computes a ``distance'' between two affine
   * transformations.  This distance is guaranteed to be a metric,
   * but not any particular metric.  (At the moment, the algorithm
   * is to collect all the elements of the matrix and offset into a
   * vector, and compute the euclidean (L2) norm of that vector.
   * Some metric which could be used to estimate the distance between
   * two points transformed by the affine transformation would be
   * more useful, but I don't have time right now to work out the
   * mathematical details.) */
  ScalarType Metric(const Self * other) const;

  /** This method computes the distance from self to the identity
   * transformation, using the same metric as the one-argument form
   * of the Metric() method. **/
  ScalarType Metric(void) const;

protected:
  /** Construct an AffineTransform object
   *
   * This method constructs a new AffineTransform object and
   * initializes the matrix and offset parts of the transformation
   * to values specified by the caller.  If the arguments are
   * omitted, then the AffineTransform is initialized to an identity
   * transformation in the appropriate number of dimensions.   **/
  AffineTransform(const MatrixType &matrix,
                  const OutputVectorType &offset);
  AffineTransform(unsigned int outputDims,
                  unsigned int paramDims);
  AffineTransform();
  
  /** Destroy an AffineTransform object   **/
  virtual ~AffineTransform();

  /** Print contents of an AffineTransform */
  void PrintSelf(std::ostream &s, Indent indent) const;

private:

  AffineTransform(const Self & other);
  const Self & operator=( const Self & );

}; //class AffineTransform

/** Back transform a vector */
template<class TScalarType, unsigned int NDimensions>
inline
typename AffineTransform<TScalarType, NDimensions>::InputVectorType
AffineTransform<TScalarType, NDimensions>::
BackTransform(const OutputVectorType &vect ) const 
{
  itkWarningMacro(<<"BackTransform(): This method is slated to be removed\
   from ITK. Instead, please use GetInverse() to generate an inverse\
   transform and then perform the transform using that inverted transform.");
  return this->GetInverseMatrix() * vect;
}


/** Back transform a vnl_vector */
template<class TScalarType, unsigned int NDimensions>
inline
typename AffineTransform<TScalarType, NDimensions>::InputVnlVectorType
AffineTransform<TScalarType, NDimensions>::
BackTransform(const OutputVnlVectorType &vect ) const 
{
  itkWarningMacro(<<"BackTransform(): This method is slated to be removed\
   from ITK. Instead, please use GetInverse() to generate an inverse\
    transform and then perform the transform using that inverted transform.");
  return this->GetInverseMatrix() * vect;
}


/** Back Transform a CovariantVector */
template<class TScalarType, unsigned int NDimensions>
inline
typename AffineTransform<TScalarType, NDimensions>::InputCovariantVectorType
AffineTransform<TScalarType, NDimensions>::
BackTransform(const OutputCovariantVectorType &vec) const 
{
  itkWarningMacro(<<"BackTransform(): This method is slated to be removed\
   from ITK. Instead, please use GetInverse() to generate an inverse\
   transform and then perform the transform using that inverted transform.");

  InputCovariantVectorType result;    // Converted vector

  for (unsigned int i = 0; i < NDimensions; i++) 
    {
    result[i] = NumericTraits<ScalarType>::Zero;
    for (unsigned int j = 0; j < NDimensions; j++) 
      {
      result[i] += this->GetMatrix()[j][i]*vec[j]; // Direct matrix transposed
      }
    }
  return result;
}


/** Back transform a given point which is represented as type PointType */
template<class TScalarType, unsigned int NDimensions>
inline
typename AffineTransform<TScalarType, NDimensions>::InputPointType
AffineTransform<TScalarType, NDimensions>::
BackTransformPoint(const OutputPointType &point) const
{
  return this->BackTransform(point);
}

/** Back transform a point */
template<class TScalarType, unsigned int NDimensions>
inline
typename AffineTransform<TScalarType, NDimensions>::InputPointType
AffineTransform<TScalarType, NDimensions>::
BackTransform(const OutputPointType &point) const 
{
  itkWarningMacro(<<"BackTransform(): This method is slated to be removed\
   from ITK.  Instead, please use GetInverse() to generate an inverse\
   transform and then perform the transform using that inverted transform.");
  InputPointType result;       // Converted point
  ScalarType temp[NDimensions];
  unsigned int i, j;

  for (j = 0; j < NDimensions; j++) 
    {
    temp[j] = point[j] - this->GetOffset()[j];
    }

  for (i = 0; i < NDimensions; i++) 
    {
    result[i] = 0.0;
    for (j = 0; j < NDimensions; j++) 
      {
      result[i] += this->GetInverseMatrix()[i][j]*temp[j];
      }
    }
  return result;
}

}  // namespace itk

// Define instantiation macro for this template.
#define ITK_TEMPLATE_AffineTransform(_, EXPORT, x, y) namespace itk { \
  _(2(class EXPORT AffineTransform< ITK_TEMPLATE_2 x >)) \
  namespace Templates { typedef AffineTransform< ITK_TEMPLATE_2 x > \
                                                  AffineTransform##y; } \
  }

#if ITK_TEMPLATE_EXPLICIT
# include "Templates/itkAffineTransform+-.h"
#endif

#if ITK_TEMPLATE_TXX
# include "itkAffineTransform.txx"
#endif

#endif /* __itkAffineTransform_h */
